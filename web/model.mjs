export const PAGE_SIZE=60;
export function intersects(a,b){return a[0]<=b[2]&&a[2]>=b[0]&&a[1]<=b[3]&&a[3]>=b[1];}
export function filterWater(features,{query='',jurisdiction='',kind='',classification='',culverts=false,bbox=null}={}){const q=query.trim().toLocaleLowerCase();return features.filter(({properties:p})=>(!q||p.name.toLocaleLowerCase().includes(q))&&(!jurisdiction||p.jurisdiction===jurisdiction)&&(!kind||p.kind===kind)&&(!classification||p.classification===classification)&&(culverts||p.kind!=='Culvert')&&(!bbox||intersects(p.bbox,bbox))).sort((a,b)=>a.properties.name.localeCompare(b.properties.name)||a.properties.id.localeCompare(b.properties.id));}
export function featureBounds(f){const b=f.properties.bbox;return [[b[1],b[0]],[b[3],b[2]]];}
