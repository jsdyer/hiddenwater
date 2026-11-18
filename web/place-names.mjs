// Local flowing-water name records from the BC Geographical Names Office, reviewed 2026-11-18.
const records = new Map([
  ["Anderson Creek", 1508],
  ["Benson Canal", 4197],
  ["Bertrand Creek", 4261],
  ["Bori Creek", 307],
  ["Cave Creek", 3455],
  ["Coghlan Creek", 10793],
  ["Howes Creek", 14852],
  ["Langley Creek", 37743],
  ["Latimer Creek", 8923],
  ["McInnis Creek", 30188],
  ["Muckle Creek", 37741],
  ["Munday Creek", 8273],
  ["Murray Creek", 8317],
  ["Nathan Creek", 9117],
  ["Newlands Brook", 37621],
  ["Nicomekl River", 14298],
  ["Palmateer Creek", 75],
  ["Pepin Creek", 53966],
  ["Pleasantdale Creek", 37618],
  ["Salmon River", 13640],
  ["Tyre Creek", 110],
  ["West Creek", 20167],
  ["Willock Brook", 37619],
  ["Yorkson Creek", 25298],
]);

export function placeNameLink(name) {
  const id = records.get(name);
  return id ? `https://coolcode.ca/bcplacenames/#name=${id}` : null;
}
