// Minimal stub for two-photo capture
export async function capturePhotos() {
  // TODO: integrate real camera flow; return two fake Blobs for now
  return { front: new Blob(['front'], {type: 'image/jpeg'}), side: new Blob(['side'], {type: 'image/jpeg'}) };
}
