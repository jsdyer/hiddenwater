import test from 'node:test';import assert from 'node:assert/strict';
import {filterWater,intersects} from '../web/model.mjs';import {csv} from '../web/common.mjs';
const f=(id,name,kind='Creek',jurisdiction='Township')=>({properties:{id,name,kind,jurisdiction,classification:'A',bbox:[-122.7,49.1,-122.6,49.2]}});
test('search, source and culvert filters compose',()=>{const rows=[f('1','Yorkson Creek'),f('2','Yorkson culvert','Culvert'),f('3','Yorkson Creek','Watercourse','City')];assert.equal(filterWater(rows,{query:' YORKSON ',jurisdiction:'Township'}).length,1);assert.equal(filterWater(rows,{culverts:true}).length,3);assert.equal(filterWater(rows,{bbox:[0,0,1,1]}).length,0);});
test('touching map bounds remain included',()=>assert.equal(intersects([0,0,1,1],[1,1,2,2]),true));
test('exports quote cells and neutralize spreadsheet formulas',()=>assert.equal(csv([['=SUM(A1)','a"b',null]]),'"\'=SUM(A1)","a""b",""'));

import {placeNameLink} from '../web/place-names.mjs';
test('local names open their reviewed provincial record', () => {
  assert.equal(placeNameLink('Yorkson Creek'), 'https://coolcode.ca/bcplacenames/#name=25298');
  assert.equal(placeNameLink('Salmon River'), 'https://coolcode.ca/bcplacenames/#name=13640');
  assert.equal(placeNameLink('Unnamed channel'), null);
});

test('named waterway links match exact names and keep ordinary text searches broad', () => {
  const rows = [f('main', 'Yorkson Creek'), f('branch', 'Yorkson Creek Tributary')];
  assert.deepEqual(filterWater(rows, {query: 'yorkson creek', exactName: true}), [rows[0]]);
  assert.equal(filterWater(rows, {query: 'yorkson creek'}).length, 2);
});
