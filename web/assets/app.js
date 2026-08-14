const examples = {
  identity: {subject:'Administrators blocked by Conditional Access',description:'Three privileged administrators cannot sign in after a policy update. They receive an access policy error and no safe workaround exists.',requester:'Identity Service Desk',affected_users:3,business_service:'Identity Platform'},
  network: {subject:'Remote employees cannot connect to VPN',description:'Multiple departments report that the VPN disconnects within two minutes. Around 95 remote employees cannot access internal applications, and the workaround is limited.',requester:'Service Desk',affected_users:95,business_service:'Remote Access'},
  security: {subject:'Suspicious sign-in and mailbox forwarding rule',description:'One employee reported an unexpected MFA prompt. Security monitoring also detected an unusual sign-in and a new external mailbox forwarding rule.',requester:'Security Hotline',affected_users:1,business_service:'Corporate IT'}
};

const knowledge = [
  ['KB-104','Access & Identity','Restore identity and access','Sign-in logs, MFA state, policy evaluation, least-privilege recovery.'],
  ['KB-207','Cloud & Infrastructure','Triage cloud workload health','Service health, deployment history, dependencies, and reversible recovery.'],
  ['KB-318','Data & Database','Investigate data degradation','Connections, capacity, locks, replication, and correctness validation.'],
  ['KB-412','Email & Collaboration','Recover collaboration services','Message trace, policies, quota, sharing, and end-to-end verification.'],
  ['KB-526','Hardware & Devices','Diagnose endpoint failure','Asset evidence, hardware diagnostics, data protection, and recovery.'],
  ['KB-631','Network & Connectivity','Isolate network path failure','Link, DHCP, DNS, routing, VPN, packet evidence, and reachability.'],
  ['KB-745','Security & Compliance','Contain security signals','Evidence preservation, scoped containment, escalation, and custody.'],
  ['KB-852','Software & Applications','Troubleshoot application errors','Reproduction, versions, configuration, dependencies, and validation.']
];

const demoQueue = [
  {ticket_id:'TF-8F4A3D11',subject:'Conditional Access block after device replacement',requester:'Executive Support',category:'Access & Identity',category_confidence:.58,priority:'P1',priority_confidence:.89,assignment_group:'Identity Operations',needs_human_review:1},
  {ticket_id:'TF-73C02B9A',subject:'Customer API returns intermittent 503 responses',requester:'Application Desk',category:'Software & Applications',category_confidence:.61,priority:'P2',priority_confidence:.54,assignment_group:'Application Support',needs_human_review:1},
  {ticket_id:'TF-2B7EAA40',subject:'Unexpected admin identity detected overnight',requester:'SOC Analyst',category:'Security & Compliance',category_confidence:.92,priority:'P1',priority_confidence:.94,assignment_group:'Security Operations Center',needs_human_review:1},
  {ticket_id:'TF-19D6CC72',subject:'Shared drive permissions missing for project team',requester:'Collaboration Desk',category:'Email & Collaboration',category_confidence:.57,priority:'P3',priority_confidence:.66,assignment_group:'Collaboration Services',needs_human_review:1},
  {ticket_id:'TF-482AC911',subject:'VPN disconnects for remote sales team',requester:'Service Desk',category:'Network & Connectivity',category_confidence:.91,priority:'P2',priority_confidence:.83,assignment_group:'Network Operations',needs_human_review:0},
  {ticket_id:'TF-31E5B20D',subject:'Nightly import rejected 42 rows',requester:'Data Operations',category:'Data & Database',category_confidence:.88,priority:'P3',priority_confidence:.78,assignment_group:'Data Services',needs_human_review:0}
];

const state = {lastPrediction:null,queue:demoQueue};
const $ = (selector, root=document) => root.querySelector(selector);
const $$ = (selector, root=document) => [...root.querySelectorAll(selector)];

function showView(name){
  $$('.view').forEach(view=>view.classList.toggle('active',view.dataset.page===name));
  $$('.rail nav button').forEach(button=>button.classList.toggle('active',button.dataset.view===name));
  $('.rail').classList.remove('open'); $('#menuButton').setAttribute('aria-expanded','false');
  location.hash=name; window.scrollTo({top:0,behavior:'smooth'});
}
$$('[data-view]').forEach(button=>button.addEventListener('click',()=>showView(button.dataset.view)));
$$('[data-jump]').forEach(button=>button.addEventListener('click',()=>showView(button.dataset.jump)));
$('#menuButton').addEventListener('click',()=>{const open=$('.rail').classList.toggle('open');$('#menuButton').setAttribute('aria-expanded',String(open));});

function percent(value){return `${Math.round(value*100)}%`}
function priorityClass(priority){return priority.toLowerCase()}
function toast(message){const node=$('#toast');node.textContent=message;node.classList.add('show');setTimeout(()=>node.classList.remove('show'),2500)}

function renderActivity(items){
  const rows=(items.length?items:demoQueue).slice(0,5);
  $('#activityRows').innerHTML=rows.map(item=>`<tr><td>${item.ticket_id}</td><td>${item.subject}</td><td><span class="tag">${item.category}</span></td><td><span class="priority-tag ${priorityClass(item.priority)}">${item.priority}</span></td><td>${percent(item.category_confidence)}</td><td>${item.needs_human_review?'<span class="review-tag">Review</span>':'Assisted route'}</td></tr>`).join('');
}

function renderQueue(items){
  state.queue=items.length?items:demoQueue;
  const query=$('#queueSearch').value.toLowerCase();
  $('#reviewQueue').innerHTML=state.queue.filter(item=>`${item.ticket_id} ${item.subject} ${item.category}`.toLowerCase().includes(query)).map(item=>`<article class="review-item"><strong>${item.ticket_id}</strong><div class="subject"><strong>${item.subject}</strong><span>${item.requester} · ${item.affected_users||1} affected</span></div><div><small>CATEGORY</small><div>${item.category}</div></div><div><span class="priority-tag ${priorityClass(item.priority)}">${item.priority}</span></div><div class="confidence"><small>${percent(item.category_confidence)} confidence</small><i><b style="width:${percent(item.category_confidence)}"></b></i></div><button data-review="${item.ticket_id}">${item.needs_human_review?'Review':'Inspect'}</button></article>`).join('');
}
$('#queueSearch').addEventListener('input',()=>renderQueue(state.queue));

function renderKnowledge(filter=''){
  const query=filter.toLowerCase();
  $('#knowledgeGrid').innerHTML=knowledge.filter(item=>item.join(' ').toLowerCase().includes(query)).map((item,index)=>`<article class="knowledge-card"><span>${item[0]} · ARTICLE ${String(index+1).padStart(2,'0')}</span><h2>${item[2]}</h2><p>${item[3]}</p><ul><li>Evidence before changes</li><li>Smallest reversible action</li><li>User-path verification</li></ul><footer><b>${item[1]}</b><span>6–9 steps</span></footer></article>`).join('');
}
$('#knowledgeSearch').addEventListener('input',event=>renderKnowledge(event.target.value));

function fillExample(name){
  const data=examples[name]; const form=$('#ticketForm');
  Object.entries(data).forEach(([key,value])=>{if(form.elements[key])form.elements[key].value=value});
  $('#charCount').textContent=form.elements.description.value.length;
}
$$('[data-example]').forEach(button=>button.addEventListener('click',()=>fillExample(button.dataset.example)));
$('#ticketForm').elements.description.addEventListener('input',event=>$('#charCount').textContent=event.target.value.length);
$('#clearForm').addEventListener('click',()=>{$('#ticketForm').reset();$('#charCount').textContent='0';$('#resultContent').classList.add('hidden');$('#resultEmpty').classList.remove('hidden')});

function showResult(result){
  state.lastPrediction=result; $('#resultEmpty').classList.add('hidden');$('#resultContent').classList.remove('hidden');
  $('#resultId').textContent=result.ticket_id;$('#resultCategory').textContent=result.category;$('#resultGroup').textContent=result.assignment_group;
  $('#resultPriority').textContent=result.priority;$('#resultSla').textContent=`${result.sla_target_minutes}-minute response target`;
  $('#categoryConfidence').textContent=percent(result.category_confidence);$('#categoryProgress').value=result.category_confidence*100;
  $('#priorityConfidence').textContent=percent(result.priority_confidence);$('#priorityProgress').value=result.priority_confidence*100;
  $('#rationaleTerms').innerHTML=result.rationale_terms.map(term=>`<b>${term}</b>`).join('');
  $('#knowledgeArticle').textContent=result.knowledge_article;$('#recommendedActions').innerHTML=result.recommended_actions.map(action=>`<li>${action}</li>`).join('');
  const review=$('#reviewState');review.textContent=result.needs_human_review?'HUMAN REVIEW':'ASSISTED ROUTE';review.classList.toggle('review',result.needs_human_review);
}

$('#ticketForm').addEventListener('submit',async event=>{
  event.preventDefault(); const button=$('.submit');button.disabled=true;button.querySelector('span').textContent='Analyzing ticket…';
  const form=new FormData(event.currentTarget);const payload=Object.fromEntries(form.entries());payload.affected_users=Number(payload.affected_users);
  try{const response=await fetch('/api/classify',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});if(!response.ok)throw new Error('Classification failed');showResult(await response.json());await loadData();toast('Classification complete — review the evidence.')}catch(error){toast('Unable to classify. Check that the API is running.')}finally{button.disabled=false;button.querySelector('span').textContent='Run intelligent triage'}
});

async function submitFeedback(accepted){
  if(!state.lastPrediction){toast('Classify a ticket first.');return}
  const response=await fetch('/api/feedback',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({ticket_id:state.lastPrediction.ticket_id,accepted,note:accepted?'Operator accepted assisted route.':'Operator requested correction.'})});
  toast(response.ok?(accepted?'Decision accepted and recorded.':'Correction request recorded.'):'Feedback could not be saved.');
}
$('#acceptPrediction').addEventListener('click',()=>submitFeedback(true));$('#correctPrediction').addEventListener('click',()=>submitFeedback(false));

function renderHeatmap(){
  const values=[.96,.08,.03,.04,.02,.07,.04,.05,.06,.93,.05,.04,.03,.08,.02,.04,.03,.04,.95,.02,.03,.04,.03,.06,.04,.03,.02,.94,.03,.05,.04,.07,.02,.03,.04,.03,.96,.04,.02,.05,.05,.06,.03,.04,.03,.92,.05,.04,.03,.02,.04,.05,.02,.04,.95,.06,.04,.04,.05,.07,.03,.05,.06,.93];
  $('#heatmapGrid').innerHTML=values.map(value=>`<i style="--a:${value}" title="${value}"></i>`).join('');
}

async function loadData(){
  try{
    const [metricsResponse,queueResponse]=await Promise.all([fetch('/api/metrics'),fetch('/api/queue')]);
    const metrics=await metricsResponse.json();const queue=await queueResponse.json();
    const reviewCount=queue.filter(item=>item.needs_human_review).length;
    $('#accuracyMetric').textContent=percent(metrics.model.category_accuracy);$('#classifiedMetric').textContent=String(metrics.operations.classified_tickets).padStart(2,'0');
    $('#reviewMetric').textContent=percent(metrics.operations.human_review_rate);$('#reviewBadge').textContent=reviewCount;$('#stageReviewCount').textContent=reviewCount;$('#openReviewCount').textContent=String(reviewCount).padStart(2,'0');$('#categoryAccuracy').textContent=percent(metrics.model.category_accuracy);$('#categoryF1').textContent=percent(metrics.model.category_macro_f1);$('#priorityAccuracy').textContent=percent(metrics.model.priority_accuracy);$('#priorityF1').textContent=percent(metrics.model.priority_macro_f1);$('#dataHash').textContent=metrics.data_hash.toUpperCase();
    renderActivity(queue);renderQueue(queue);
  }catch(error){renderActivity(demoQueue);renderQueue(demoQueue)}
}

document.addEventListener('keydown',event=>{if((event.metaKey||event.ctrlKey)&&event.key==='Enter'&&$('.view[data-page="classify"]').classList.contains('active'))$('#ticketForm').requestSubmit()});
const initial=location.hash.replace('#','');if(initial&&$(`[data-page="${initial}"]`))showView(initial);
if(new URLSearchParams(location.search).get('demo')==='result'){showView('classify');setTimeout(()=>$('#ticketForm').requestSubmit(),350)}
renderKnowledge();renderHeatmap();renderActivity(demoQueue);renderQueue(demoQueue);loadData();
