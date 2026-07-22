(function () {
  'use strict';

  const ENDPOINT = '/events/usage';
  const SCHEMA_VERSION = 'usage-event-v1';
  const startedAt = Date.now();
  const nativeFetch = window.fetch.bind(window);
  const uuid = () => (globalThis.crypto?.randomUUID?.() ||
    'evt-' + Date.now().toString(36) + '-' + Math.random().toString(36).slice(2));

  let sessionId = sessionStorage.getItem('phyllos_usage_session');
  if (!sessionId) {
    sessionId = uuid();
    sessionStorage.setItem('phyllos_usage_session', sessionId);
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
      page: location.pathname,
      component: details?.component || null,
      action: details?.action || null,
      metadata: details?.metadata || {},
      occurred_at: new Date().toISOString()
    };
    const body = JSON.stringify(payload);
    if (navigator.sendBeacon) {
      navigator.sendBeacon(ENDPOINT, new Blob([body], { type: 'application/json' }));
      return;
    }
    nativeFetch(ENDPOINT, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body, keepalive: true })
      .catch(() => {});
  }

  window.PhyllosTelemetry = { track: send };

  window.fetch = async function (input, init) {
    const response = await nativeFetch(input, init);
    const url = typeof input === 'string' ? input : input?.url || '';
    if (!response.ok) {
      send('api_error', {
        component: 'fetch', action: 'response',
        metadata: { status_code: response.status, step: 'request' }
      });
    } else if (/\/dpp\/publicar(?:\?|$)/.test(url)) {
      send('flow_complete', {
        component: 'dpp_publication', action: 'complete', metadata: { flow: 'publish_dpp' }
      });
    }
    return response;
  };

  document.addEventListener('DOMContentLoaded', () => {
    send('page_view', {
      component: 'document',
      action: 'view',
      metadata: { viewport_width: innerWidth, viewport_height: innerHeight }
    });
  });

  document.addEventListener('click', (event) => {
    const target = event.target.closest('button, a, [role="button"], [data-telemetry]');
    if (!target) return;
    send('ui_click', {
      component: componentName(target),
      action: target.tagName === 'A' ? 'navigate' : 'activate',
      metadata: { target_type: target.tagName.toLowerCase() }
    });
  }, true);

  document.addEventListener('submit', (event) => {
    send('form_submit', {
      component: componentName(event.target),
      action: 'submit',
      metadata: { form_id: event.target.id || event.target.getAttribute('name') || 'anonymous' }
    });
  }, true);

  document.addEventListener('change', (event) => {
    const target = event.target;
    if (!target.matches('input, select, textarea')) return;
    send('field_change', {
      component: componentName(target),
      action: 'change',
      metadata: { field_type: target.type || target.tagName.toLowerCase() }
    });
  }, true);

  window.addEventListener('error', (event) => {
    send('js_error', { component: 'window', action: 'error', metadata: { step: event.filename ? 'script' : 'runtime' } });
  });

  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState !== 'hidden') return;
    send('visibility_end', {
      component: 'document',
      action: 'hide',
      metadata: { duration_ms: Date.now() - startedAt, visibility_state: document.visibilityState }
    });
  });
})();
