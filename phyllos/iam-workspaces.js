(() => {
  const $ = selector => document.querySelector(selector);
  const all = selector => [...document.querySelectorAll(selector)];
  const esc = value => String(value ?? '').replace(/[&<>'"]/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'})[char]);
  const sessionId = sessionStorage.getItem('phyllos-iam-session') || crypto.randomUUID();
  sessionStorage.setItem('phyllos-iam-session', sessionId);
  let state = { people: [], workspaces: [], memberships: [] };

  const notify = message => { const toast=$('#toast'); toast.textContent=message; toast.classList.add('show'); setTimeout(()=>toast.classList.remove('show'),2800); };
  const bucket = count => count === 0 ? '0' : count <= 5 ? '1-5' : count <= 20 ? '6-20' : count <= 50 ? '21-50' : '51+';

  async function api(path, options={}) {
    const response = await fetch(path, {credentials:'same-origin', headers:{'Content-Type':'application/json','X-Request-ID':crypto.randomUUID(),...(options.headers||{})}, ...options});
    if (!response.ok) {
      const body = await response.json().catch(()=>({}));
      throw new Error(body.detail || `Falha na operação (${response.status})`);
    }
    return response.status === 204 ? null : response.json();
  }

  function track(eventName, properties={}) {
    const payload = {
      event_id: crypto.randomUUID(), schema_version:'usage-event-v3', event_version:1,
      session_id: sessionId, event_name:eventName, page:'/workspace',
      component:'iam_console', action:'intent', metadata:properties,
      occurred_at:new Date().toISOString(), source:'web', environment:'production'
    };
    fetch('/events/usage', {method:'POST',headers:{'Content-Type':'application/json'},credentials:'same-origin',body:JSON.stringify(payload),keepalive:true}).catch(()=>{});
  }

  function trackOnce(key, eventName, properties={}) {
    if (sessionStorage.getItem(key)) return;
    sessionStorage.setItem(key, '1'); track(eventName, properties);
  }

  function person(id){ return state.people.find(item=>item.id===id); }
  function workspace(id){ return state.workspaces.find(item=>item.id===id); }

  function renderSummary(){
    const active=state.people.filter(item=>item.status==='active').length;
    const pending=state.people.filter(item=>item.status==='pending').length;
    $('#iamSummary').innerHTML=[['Pessoas ativas',active],['Convites pendentes',pending],['Workspaces',state.workspaces.filter(item=>item.status==='active').length],['Acessos ativos',state.memberships.length]].map(([label,value])=>`<article><span>${label}</span><strong>${value}</strong></article>`).join('');
  }

  function renderPeople(){
    $('#iamPeopleList').innerHTML=state.people.length?state.people.map(item=>`<div class="iam-person"><div><strong>${esc(item.display_name)}</strong><small>${esc(item.email)}</small></div><span>${esc(item.category)}</span><span class="iam-status ${esc(item.status)}">${esc(item.status)}</span><button class="link iam-archive-person" data-person="${esc(item.id)}" ${item.status==='archived'?'disabled':''}>Arquivar</button></div>`).join(''):'<div class="iam-empty">Nenhuma pessoa cadastrada.</div>';
    all('.iam-archive-person').forEach(button=>button.addEventListener('click',async()=>{ try{await api(`/pessoas/${button.dataset.person}`,{method:'PATCH',body:JSON.stringify({status:'archived'})});await loadAll();notify('Pessoa arquivada');}catch(error){notify(error.message);} }));
  }

  function renderWorkspaces(){
    $('#iamWorkspaceList').innerHTML=state.workspaces.length?state.workspaces.map(item=>{const members=state.memberships.filter(access=>access.workspace_id===item.id).length;return`<article class="iam-workspace-card"><span class="iam-status ${esc(item.status)}">${item.workspace_type==='team'?'Equipe':'Individual'}</span><h3>${esc(item.name)}</h3><p>${members} membro(s) ativo(s)</p><footer><button class="link iam-open-access" data-workspace="${esc(item.id)}">Gerenciar acesso →</button><button class="link iam-archive-workspace" data-workspace="${esc(item.id)}" ${item.status==='archived'?'disabled':''}>Arquivar</button></footer></article>`;}).join(''):'<div class="iam-empty">Crie o primeiro workspace.</div>';
    all('.iam-open-access').forEach(button=>button.addEventListener('click',()=>{openTab('access');$('#iamAccessForm').elements.workspace_id.value=button.dataset.workspace;}));
    all('.iam-archive-workspace').forEach(button=>button.addEventListener('click',async()=>{try{await api(`/workspaces/${button.dataset.workspace}`,{method:'PATCH',body:JSON.stringify({status:'archived'})});await loadAll();notify('Workspace arquivado');}catch(error){notify(error.message);}}));
  }

  function renderAccess(){
    const personSelect=$('#iamAccessForm').elements.person_id, workspaceSelect=$('#iamAccessForm').elements.workspace_id;
    personSelect.innerHTML='<option value="">Selecione</option>'+state.people.filter(item=>item.status!=='archived').map(item=>`<option value="${esc(item.id)}">${esc(item.display_name)} · ${esc(item.email)}</option>`).join('');
    workspaceSelect.innerHTML='<option value="">Selecione</option>'+state.workspaces.filter(item=>item.status==='active').map(item=>`<option value="${esc(item.id)}">${esc(item.name)}</option>`).join('');
    $('#iamAccessList').innerHTML=state.memberships.length?state.memberships.map(item=>`<div class="iam-membership"><div><strong>${esc(item.person.display_name)}</strong><small>${esc(item.person.email)}</small></div><div><strong>${esc(workspace(item.workspace_id)?.name||'Workspace')}</strong><small>Membership persistente</small></div><select class="iam-role" data-workspace="${esc(item.workspace_id)}" data-membership="${esc(item.id)}"><option value="viewer" ${item.role==='viewer'?'selected':''}>viewer</option><option value="member" ${item.role==='member'?'selected':''}>member</option><option value="admin" ${item.role==='admin'?'selected':''}>admin</option><option value="owner" ${item.role==='owner'?'selected':''}>owner</option></select><button class="link iam-remove-access" data-workspace="${esc(item.workspace_id)}" data-membership="${esc(item.id)}">Remover</button></div>`).join(''):'<div class="iam-empty">Nenhuma membership ativa.</div>';
    all('.iam-role').forEach(select=>select.addEventListener('change',async()=>{try{await api(`/workspaces/${select.dataset.workspace}/members/${select.dataset.membership}`,{method:'PATCH',body:JSON.stringify({role:select.value})});await loadAll();notify('Papel atualizado');}catch(error){notify(error.message);await loadAll();}}));
    all('.iam-remove-access').forEach(button=>button.addEventListener('click',async()=>{try{await api(`/workspaces/${button.dataset.workspace}/members/${button.dataset.membership}`,{method:'DELETE'});await loadAll();notify('Acesso removido');}catch(error){notify(error.message);}}));
  }

  function renderAll(){renderSummary();renderPeople();renderWorkspaces();renderAccess();}

  async function loadAll(){
    try{
      const [people,workspaces]=await Promise.all([api('/pessoas'),api('/workspaces')]);
      const memberGroups=await Promise.all(workspaces.map(item=>api(`/workspaces/${item.id}/members`)));
      state={people,workspaces,memberships:memberGroups.flat()}; renderAll();
      trackOnce('phyllos-person-list-viewed','person_list_viewed',{result_count_bucket:bucket(people.length),filter_category:'all'});
    }catch(error){notify(error.message);}
  }

  function openTab(tab){
    all('[data-iam-tab]').forEach(button=>button.classList.toggle('active',button.dataset.iamTab===tab));
    for(const name of ['people','workspaces','access']) $(`#iam${name[0].toUpperCase()+name.slice(1)}Panel`).classList.toggle('hidden',name!==tab);
    if(tab==='access') trackOnce('phyllos-member-list-viewed','workspace_member_list_viewed');
  }

  all('[data-iam-tab]').forEach(button=>button.addEventListener('click',()=>openTab(button.dataset.iamTab)));
  $('#openIamUser').addEventListener('click',()=>{$('#iamUserForm').classList.remove('hidden');track('person_creation_started',{creation_source:'admin_console'});});
  $('#openIamWorkspace').addEventListener('click',()=>{$('#iamWorkspaceForm').classList.remove('hidden');track('workspace_creation_started',{creation_source:'admin_console'});});
  all('[data-iam-cancel]').forEach(button=>button.addEventListener('click',()=>button.closest('form').classList.add('hidden')));

  $('#iamUserForm').addEventListener('submit',async event=>{event.preventDefault();const data=Object.fromEntries(new FormData(event.currentTarget));try{await api('/pessoas',{method:'POST',body:JSON.stringify(data)});event.currentTarget.reset();event.currentTarget.classList.add('hidden');await loadAll();notify('Pessoa cadastrada');}catch(error){notify(error.message);}});
  $('#iamWorkspaceForm').addEventListener('submit',async event=>{event.preventDefault();const data=Object.fromEntries(new FormData(event.currentTarget));try{await api('/workspaces',{method:'POST',body:JSON.stringify(data)});event.currentTarget.reset();event.currentTarget.classList.add('hidden');await loadAll();notify('Workspace criado');}catch(error){notify(error.message);}});
  $('#iamAccessForm').addEventListener('submit',async event=>{event.preventDefault();const data=Object.fromEntries(new FormData(event.currentTarget));track('workspace_member_invitation_started',{invited_role:data.role,invitation_source:'admin_console'});try{const result=await api(`/workspaces/${data.workspace_id}/invitations`,{method:'POST',body:JSON.stringify({person_id:data.person_id,role:data.role})});const box=$('#invitationResult');box.classList.remove('hidden');box.innerHTML=`Convite criado. Token de uso único: <code>${esc(result.invitation_token)}</code> <button class="link" id="copyInvitation">Copiar</button>`;$('#iamAcceptForm').elements.token.value=result.invitation_token;$('#copyInvitation').addEventListener('click',()=>navigator.clipboard.writeText(result.invitation_token));notify('Convite persistido');}catch(error){notify(error.message);}});
  $('#iamAcceptForm').addEventListener('submit',async event=>{event.preventDefault();const token=new FormData(event.currentTarget).get('token').trim();try{await api(`/invitations/${encodeURIComponent(token)}/accept`,{method:'POST',body:'{}'});event.currentTarget.reset();$('#invitationResult').classList.add('hidden');await loadAll();notify('Convite aceito e membership criada');}catch(error){notify(error.message);}});

  loadAll();
})();
