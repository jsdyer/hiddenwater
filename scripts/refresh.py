"""Refresh the reference map; offline builds always use the last reviewed snapshot."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import gzip
import json
from pathlib import Path
from source import features, bounds

ROOT=Path(__file__).resolve().parents[1]
BASE='https://services5.arcgis.com/frpHL0Fv8koQRVWY/arcgis/rest/services/'
SOURCES=[
 {'id':'channels','name':'Township drainage channels','url':BASE+'Drainage_Channels/FeatureServer/0','fields':'OBJECTID,GlobalID,Id_Channel,Channel_Name,Channel_Type_Desc,Classification_Desc,Shape__Length'},
 {'id':'culverts','name':'Township drainage culverts','url':BASE+'Drainage_Culverts/FeatureServer/0','fields':'OBJECTID,GlobalID,Id_Pipe,Culvert_Type_Desc,Lifecycle_Status,Material,Shape__Length'},
 {'id':'city','name':'Langley City watercourse classifications','url':'https://maps.langleycity.ca/server/rest/services/Maps/Open_Data/MapServer/185','fields':'OBJECTID,NAME,CLASSIFICATION,JURISDICTION'}
]

def normalize(feature, source):
    p=feature['properties'];kind=source['id']
    if kind=='channels':
        name=p.get('Channel_Name') or 'Unnamed channel'
        category=p.get('Channel_Type_Desc') or 'Channel'
        classification=(p.get('Classification_Desc') or 'Unclassified').replace('UNOFFICAL ','').replace('UNOFFICIAL ','')
        reference=True
    elif kind=='culverts':
        name='Culvert '+str(p.get('Id_Pipe') or p['OBJECTID']);category='Culvert'
        classification='Not classified';reference=False
    else:
        name=p.get('NAME') or 'Unnamed watercourse';category='Watercourse'
        classification={1:'Class A',2:'Class A(O)',3:'Class B',4:'Class C'}.get(p.get('CLASSIFICATION'),'Unclassified');reference=False
    return {'type':'Feature','geometry':feature['geometry'],'properties':{
        'id':kind+':'+str(p.get('GlobalID') or p['OBJECTID']), 'name':name.strip(),
        'kind':category,'classification':classification,'unofficial':reference,
        'jurisdiction':'City' if kind=='city' else 'Township','source':kind,
        'record_id':p['OBJECTID'],'length_m':round(p.get('Shape__Length') or 0),
        'material':p.get('Material') or '', 'lifecycle':p.get('Lifecycle_Status') or '',
        'bbox':bounds(feature['geometry'])}}

def main():
    def load(s):return [normalize(f,s) for f in features(s['url'],s['fields'])]
    with ThreadPoolExecutor(max_workers=3) as pool: groups=list(pool.map(load,SOURCES))
    output=ROOT/'web/data/water.json.gz';output.parent.mkdir(exist_ok=True)
    data={'retrieved_at':datetime.now(timezone.utc).isoformat(),'sources':[{k:v for k,v in s.items() if k!='fields'} for s in SOURCES],
          'type':'FeatureCollection','features':sum(groups,[])}
    if len(data['features'])<1000:raise ValueError('Source unexpectedly small')
    if output.exists():
        with gzip.open(output, "rt", encoding="utf-8") as previous_snapshot:
            previous=json.load(previous_snapshot)
        for source, group in zip(SOURCES,groups):
            old=sum(f['properties']['source']==source['id'] for f in previous['features'])
            if old and len(group)<old*.8:raise ValueError(source['name']+' lost over 20%; review the source before replacing it')
    stage = output.with_suffix('.tmp')
    payload = (json.dumps(data, separators=(',', ':'), ensure_ascii=False) + '\n').encode('utf-8')
    stage.write_bytes(gzip.compress(payload, mtime=0))
    stage.replace(output)
    print('Refreshed',len(data['features']),'mapped segments')

if __name__=='__main__':main()
