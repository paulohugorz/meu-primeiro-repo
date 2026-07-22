(function () {
  'use strict';

  const ENDPOINT = '/events/usage';
  const SCHEMA_VERSION = 'usage-event-v2';
  const startedAt = Date.now();
  const nativeFetch = window.fetch.bind(window);
  const uuid = () => (globalThis.crypto?.randomUUID?.() ||
    'evt-' + Date.now().toString(36) + '-' + Math.random().toString(36).slice(2));

  let sessionId = sessionStorage.getItem('phyllos_usage_session');
  if (!sessionId) {
    sessionId = uuid();
    sessionStorage.setItem('phyllos_usage_session', sessionId);
  }

  let publicationBlockedAt = Number(sessionStorage.getItem('phyllos_publication_blocked_at') || 0);

  function surface() {
    if (/^\/p\//.test(location.pathname)) return 'public_passport';
    if (/\/etiqueta$/.test(location.pathname)) return 'label';
    if (location.pathname === '/atelier') return 'atelier';
    return 'studio';
  }

  function componentName(element) {
    return element?.dataset?.telemetry || element?.id || element?.getAttribute?.('name') ||
      element?.getAttribute?.('role') || element?.tagName?.toLowerCase() || 'unknown';
  }

  function send(eventName, details) {
    const payload = {
      event_id: uuid(),
      schema_version: SCHEMA_VERSION,
      session_id: sessionId,
      event_name: eventName,
      page: normalizedPage(),
      component: details?.component || null,
      action: details?.action || null,
      metadata: { surface: surface(), ...(details?.metadata || {}) },
      occurred_at: new Date().toISOString()
    };
    const body = JSON.stringify(payload);
    if (navigator.sendBeacon) {
      navigator.sendBeacon(ENDPOINT, new Blob([body], { type: 'application/json' }));
      return;
    }
    nativeFetch(ENDPOINT, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body, keepalive: true
    }).catch(() => {});
  }

  function normalizedPage() {
    if (/^\/p\/[^/]+$/.test(location.pathname)) return '/p/:id';
    if (/^\/pecas\/[^/]+\/etiqueta$/.test(location.pathname)) return '/pecas/:id/etiqueta';
    return location.pathname;
  }

  window.PhyllosTelemetry = { track: send, schemaVersion: SCHEMA_VERSION };

  function requestDescriptor(method, pathname) {
    if (method === 'POST' && pathname === '/pecas') {
      return { started: 'piece_create_started', success: 'piece_created', failure: 'piece_create_failed', flow: 'piece_creation' };
    }
    if (method === 'PATCH' && /^\/pecas\/[^/]+$/.test(pathname)) {
      return { success: 'technical_sheet_saved', failure: 'technical_sheet_save_failed', flow: 'technical_sheet' };
    }
    if ((method === 'POST' || method === 'PATCH') && /^\/fichas-tecnicas(?:\/[^/]+)?$/.test(pathname)) {
      return { success: 'material_sheet_saved', failure: 'material_sheet_save_failed', flow: 'material_sheet' };
    }
    if (method === 'POST' && /^\/pecas\/[^/]+\/etapas-producao$/.test(pathname)) {
      return {
        started: 'production_stage_add_started', success: 'production_stage_added',
        failure: 'production_stage_add_failed', flow: 'production_stage'
      };
    }
    if (method === 'POST' && /^\/pecas\/[^/]+\/dpp\/publicar$/.test(pathname)) {
      return {
        started: 'dpp_publication_started', success: 'dpp_published',
        failure: 'dpp_publication_blocked', flow: 'dpp_publication', blocked: true
      };
    }
    if (method === 'GET' && (/^\/pecas\/[^/]+\/qr$/.test(pathname) || /^\/dpp\/[^/]+\/qr$/.test(pathname))) {
      return { started: 'qr_requested', success: 'qr_served', failure: 'qr_request_failed', flow: 'qr_access' };
    }
    return null;
  }

  function stableErrorCode(status, blocked) {
    if (blocked && status === 422) return 'validation_failed';
    if (status === 400) return 'invalid_request';
    if (status === 401 || status === 403) return 'access_denied';
    if (status === 404) return 'not_found';
    if (status === 409) return 'conflict';
    if (status === 422) return 'unprocessable';
    if (status === 429) return 'rate_limited';
    if (status >= 500) return 'server_error';
    return 'request_failed';
  }

  async function validationIssueCount(response) {
    try {
      const payload = await response.clone().json();
      const errors = payload?.detail?.errors;
      return Array.isArray(errors) ? errors.length : 0;
    } catch (_) {
      return 0;
    }
  }

  window.fetch = async function (input, init) {
    const rawUrl = typeof input === 'string' ? input : input?.url || '';
    const url = new URL(rawUrl, location.origin);
    const method = String(init?.method || (typeof input !== 'string' && input?.method) || 'GET').toUpperCase();
    const descriptor = url.origin === location.origin ? requestDescriptor(method, url.pathname) : null;
    const requestStartedAt = Date.now();

    if (descriptor?.started) {
      send(descriptor.started, {
        component: descriptor.flow,
        action: 'request',
        metadata: { flow: descriptor.flow, step: 'request', method }
      });
    }

    try {
      const response = await nativeFetch(input, init);
      if (descriptor && response.ok) {
        send(descriptor.success, {
          component: descriptor.flow,
          action: 'complete',
          metadata: {
            flow: descriptor.flow, step: 'complete', outcome: 'success', method,
            status_code: response.status, duration_ms: Date.now() - requestStartedAt
          }
        });
        if (descriptor.success === 'dpp_published' && publicationBlockedAt) {
          send('dpp_publication_recovered', {
            component: descriptor.flow,
            action: 'recover',
            metadata: {
              flow: descriptor.flow, step: 'recover', outcome: 'success', method,
              duration_ms: Date.now() - publicationBlockedAt
            }
          });
          publicationBlockedAt = 0;
          sessionStorage.removeItem('phyllos_publication_blocked_at');
        }
      } else if (descriptor) {
        const issueCount = descriptor.blocked ? await validationIssueCount(response) : 0;
        send(descriptor.failure, {
          component: descriptor.flow,
          action: descriptor.blocked ? 'blocked' : 'fail',
          metadata: {
            flow: descriptor.flow,
            step: descriptor.blocked ? 'validation' : 'request',
            outcome: descriptor.blocked ? 'blocked' : 'failure',
            error_code: stableErrorCode(response.status, descriptor.blocked),
            status_code: response.status,
            validation_issue_count: issueCount,
            method,
            duration_ms: Date.now() - requestStartedAt
          }
        });
        if (descriptor.blocked) {
          publicationBlockedAt = Date.now();
          sessionStorage.setItem('phyllos_publication_blocked_at', String(publicationBlockedAt));
        }
      } else if (!response.ok && url.pathname !== ENDPOINT) {
        send('api_action_failed', {
          component: 'fetch', action: 'fail',
          metadata: {
            flow: 'api_request', step: 'request', outcome: 'failure', method,
            error_code: stableErrorCode(response.status, false), status_code: response.status,
            duration_ms: Date.now() - requestStartedAt
          }
        });
      }
      return response;
    } catch (error) {
      if (url.pathname !== ENDPOINT) {
        send(descriptor?.failure || 'api_action_failed', {
          component: descriptor?.flow || 'fetch', action: 'fail',
          metadata: {
            flow: descriptor?.flow || 'api_request', step: 'network', outcome: 'failure',
            error_code: 'network_error', method, duration_ms: Date.now() - requestStartedAt
          }
        });
      }
      throw error;
    }
  };

  function semanticClick(target) {
    const onclick = target.getAttribute?.('onclick') || '';
    const href = target.getAttribute?.('href') || '';
    const id = target.id || '';

    if (/irParaValidar/.test(onclick) || id === 'ns-validar') {
      return ['publication_readiness_viewed', 'publication_readiness', 'view'];
    }
    if (/copiarLinkPassaporte/.test(onclick)) return null; // resultado emitido por evento do clipboard
    if (/toggleQrPreview/.test(onclick)) {
      const opening = !document.getElementById('dpp-qr-preview')?.classList.contains('visible');
      return [opening ? 'qr_preview_opened' : 'qr_preview_closed', 'qr_preview', opening ? 'open' : 'close'];
    }
    if (/imprimirEtiqueta/.test(onclick) || /\/etiqueta$/.test(href)) {
      return ['label_print_requested', 'label', 'print'];
    }
    return null;
  }

  document.addEventListener('DOMContentLoaded', () => {
    const currentSurface = surface();
    if (currentSurface === 'public_passport') {
      send('public_passport_viewed', {
        component: 'public_passport', action: 'view',
        metadata: { flow: 'public_passport', step: 'entry' }
      });
    } else if (currentSurface === 'label') {
      send('label_viewed', { component: 'label', action: 'view', metadata: { flow: 'label', step: 'entry' } });
    } else {
      send('workspace_viewed', {
        component: 'workspace', action: 'view',
        metadata: { flow: 'workspace', step: 'entry' }
      });
    }

    const qrImages = document.querySelectorAll('#dpp-qr-img, #pass-qr');
    qrImages.forEach((image) => {
      image.addEventListener('load', () => send('qr_served', {
        component: image.id, action: 'load',
        metadata: { flow: 'qr_access', step: 'complete', outcome: 'success', method: 'GET' }
      }));
      image.addEventListener('error', () => send('qr_request_failed', {
        component: image.id, action: 'fail',
        metadata: {
          flow: 'qr_access', step: 'load', outcome: 'failure', error_code: 'image_load_failed', method: 'GET'
        }
      }));
    });

    if (currentSurface === 'public_passport' && 'IntersectionObserver' in window) {
      const viewedSections = new Set();
      const sectionNames = ['supply_chain', 'impact', 'circularity', 'composition', 'circularity'];
      const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          const index = Array.from(document.querySelectorAll('#track .card')).indexOf(entry.target);
          const section = sectionNames[index];
          if (!section || viewedSections.has(section)) return;
          viewedSections.add(section);
          send('public_passport_section_viewed', {
            component: 'passport_card', action: 'view',
            metadata: { flow: 'public_passport', step: 'view', section }
          });
        });
      }, { threshold: 0.6 });
      document.querySelectorAll('#track .card').forEach((card) => observer.observe(card));
    }
  });

  document.addEventListener('click', (event) => {
    const target = event.target.closest('button, a, [role="button"], [data-telemetry]');
    if (!target) return;
    const semantic = semanticClick(target);
    if (!semantic) return;
    send(semantic[0], {
      component: componentName(target), action: semantic[2],
      metadata: { flow: semantic[1], step: semantic[2] }
    });
  }, true);

  window.addEventListener('error', () => {
    send('js_error', {
      component: 'window', action: 'error',
      metadata: { flow: 'interface', step: 'runtime', outcome: 'failure', error_code: 'runtime_error' }
    });
  });

  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState !== 'hidden' || surface() !== 'public_passport') return;
    send('public_passport_session_ended', {
      component: 'public_passport', action: 'hide',
      metadata: { flow: 'public_passport', step: 'exit', duration_ms: Date.now() - startedAt }
    });
  });
})();
