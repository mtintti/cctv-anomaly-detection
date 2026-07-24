interface StationsRes {
  features: Station[];
}

export async function get_Stations(): Promise<StationsRes> {
  const res = await fetch("http://localhost:8000/stations", {
    cache: "force-cache",
  });

  return res.json();
}