import {$,el,link,download,csv,share,baseMap,fillSelect,dateLabel} from './common.mjs';
import {placeNameLink} from './place-names.mjs';
import {filterWater,featureBounds,PAGE_SIZE} from './model.mjs';
const PLACES={willoughby:[49.158,-122.657,14],walnut:[49.178,-122.647,14],fort:[49.169,-122.578,14],city:[49.102,-122.657,14]};
const map=baseMap('map',PLACES.willoughby.slice(0,2),14);let data,results=[],page=0,selected=null,layer;
const places = [...document.querySelectorAll('[data-place]')];
const emptyDetail = $('detail').cloneNode(true);

function updateMapArea() {
  const center = map.getCenter();
  const place = places.find(button => center.distanceTo(PLACES[button.dataset.place].slice(0, 2)) < 100);
  $('map-area').textContent = place ? place.textContent + ' waterways' : 'Waterways in this map view';
  for (const button of places) button.setAttribute('aria-pressed', String(button === place));
}

function clearSelection() {
  selected = null;
  highlight.clearLayers();
  $('detail').replaceChildren(...emptyDetail.cloneNode(true).childNodes);
}

const highlight=L.geoJSON(null,{style:{color:'#142f38',weight:7,opacity:.9}}).addTo(map);
function params(){const b=map.getBounds();return {query:$('query').value,jurisdiction:$('jurisdiction').value,kind:$('kind').value,classification:$('classification').value,culverts:$('culverts').checked,bbox:$('in-view').checked?[b.getWest(),b.getSouth(),b.getEast(),b.getNorth()]:null};}
function render(){if(!data)return;results=filterWater(data.features,params());page=Math.min(page,Math.max(0,Math.ceil(results.length/PAGE_SIZE)-1));$('count').textContent=results.length.toLocaleString();$('status').textContent=results.length?'Select a segment to inspect its source record.':'No matching segments. Try a wider view or clear the filters.';for(const id of ['csv','geojson'])$(id).disabled=!results.length;
const b=map.getBounds();const visible=results.filter(f=>b.intersects(featureBounds(f))).slice(0,6000);if(layer)layer.remove();layer=L.geoJSON(visible,{style:f=>({color:f.properties.kind==='Culvert'?'#b66b35':f.properties.jurisdiction==='City'?'#8064a0':'#206a7b',weight:f.properties.kind==='Culvert'?4:2.5,opacity:.85}),onEachFeature:(f,l)=>{l.bindTooltip(el('span',f.properties.name));l.on('click',()=>select(f));}}).addTo(map);highlight.bringToFront();if(visible.length===6000)$('status').textContent='Zoom in for all map segments. Results and exports include every match.';
$('results').replaceChildren();for(const f of results.slice(page*PAGE_SIZE,(page+1)*PAGE_SIZE)){const p=f.properties;const button=el('button','','result');button.setAttribute('aria-pressed',String(selected===p.id));button.append(el('strong',p.name),el('small',`${p.jurisdiction} · ${p.kind} · ${p.classification}`));button.onclick=()=>{select(f,true);if(matchMedia('(max-width:680px)').matches)$('detail').scrollIntoView({block:'start'});};$('results').append(button);}$('prev').disabled=page===0;$('next').disabled=(page+1)*PAGE_SIZE>=results.length;$('page-label').textContent=results.length?`${page+1} / ${Math.ceil(results.length/PAGE_SIZE)}`:'0 / 0';}
function select(f,zoom=false){selected=f.properties.id;const p=f.properties;highlight.clearLayers().addData(f);if(zoom)map.fitBounds(featureBounds(f),{maxZoom:17,padding:[35,35]});const d=$('detail');d.replaceChildren(el('span',`${p.jurisdiction} · ${p.kind}`,'badge'),el('h2',p.name));const dl=el('dl','','detail-grid');for(const [k,v] of [['Published classification',p.classification],['Mapped length',p.length_m?`${p.length_m.toLocaleString()} m`:'Not supplied'],['Source record',p.record_id],['Material',p.material||'Not supplied'],['Lifecycle',p.lifecycle||'Not supplied']]){const cell=el('div');cell.append(el('dt',k),el('dd',v));dl.append(cell);}d.append(dl);if(p.unofficial)d.append(el('p','The Township labels this channel classification unofficial. It does not establish present-day fish occupancy.'));const actions=el('div','','actions');const source=data.sources.find(s=>s.id===p.source);actions.append(link('Open municipal source record ↗',`${source.url}/query?where=OBJECTID%3D${p.record_id}&outFields=*&returnGeometry=false&f=pjson`));const nameUrl = placeNameLink(p.name);
if (nameUrl) {
  actions.append(link('Explore this name in BC Place Names ↗', nameUrl));
} else if (p.name && !p.name.startsWith('Unnamed ') && p.kind !== 'Culvert') {
  actions.append(link('Search BC Place Names ↗', 'https://coolcode.ca/bcplacenames/'));
}
const button=el('button','Share this segment');button.onclick=()=>share({record:p.id});actions.append(button);d.append(actions);render();}
$('filters').onsubmit=e=>{e.preventDefault();page=0;render();if(!$('in-view').checked&&results.length)map.fitBounds(L.latLngBounds(results.flatMap(featureBounds)),{maxZoom:15});};for(const id of ['jurisdiction','kind','classification','culverts','in-view'])$(id).onchange=()=>{page=0;render();};map.on('moveend',()=>{updateMapArea();page=0;render();});updateMapArea();for(const b of document.querySelectorAll('[data-place]'))b.onclick=()=>{clearSelection();const v=PLACES[b.dataset.place];for(const id of ['query','jurisdiction','kind','classification'])$(id).value='';$('in-view').checked=true;map.setView(v.slice(0,2),v[2]);render();};$('reset').onclick=()=>places.find(button=>button.dataset.place==='willoughby').click();$('prev').onclick=()=>{page--;render();};$('next').onclick=()=>{page++;render();};$('geojson').onclick=()=>download('hidden-water.geojson',JSON.stringify({type:'FeatureCollection',retrieved_at:data.retrieved_at,sources:data.sources,features:results}));$('csv').onclick=()=>download('hidden-water.csv',csv([['name','municipality','type','classification','unofficial','source_record','snapshot_date'],...results.map(f=>{const p=f.properties;return[p.name,p.jurisdiction,p.kind,p.classification,p.unofficial,p.record_id,data.retrieved_at];})]),'text/csv');
try{const response=await fetch('./data/water.json');if(!response.ok)throw Error('Snapshot unavailable');data=await response.json();fillSelect('kind',data.features.map(f=>f.properties.kind));fillSelect('classification',data.features.map(f=>f.properties.classification));$('freshness').textContent=`Reference snapshot retrieved ${dateLabel(data.retrieved_at)}. This is the retrieval date, not each segment’s survey date.`;for(const s of data.sources){const li=el('li');li.append(link(s.name,s.url));$('sources').append(li);}render();const id=new URLSearchParams(location.hash.slice(1)).get('record');const f=data.features.find(f=>f.properties.id===id);if(f){$('culverts').checked=f.properties.kind==='Culvert';select(f,true);}}catch(e){$('water-error').hidden=false;$('status').classList.add('error');$('status').textContent='The map snapshot could not load. Please reload or use the official source links below.';}
