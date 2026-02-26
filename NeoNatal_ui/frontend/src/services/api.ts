const BASE_URL = import.meta.env.VITE_API_URL   ;

export async function getMotion() {
  const res = await fetch(`${BASE_URL}/api/motion`);
  return res.json();
}

export async function getCry() {
  const res = await fetch(`${BASE_URL}/api/cry`);
  return res.json();
}

export async function getStatus() {
  const res = await fetch(`${BASE_URL}/api/status`);
  return res.json();
}
