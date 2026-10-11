type Rgba = [red: number, green: number, blue: number, alpha: number];

export const ROAD_DAMAGE_CLASSES: Record<number, { name: string; rgba: Rgba }> = {
  0: { name: "alligator crack", rgba: [121, 212, 119, 255] },
  1: { name: "longitudinal crack", rgba: [234, 184, 133, 255] },
  2: { name: "pothole", rgba: [96, 112, 160, 255] },
  3: { name: "transverse crack", rgba: [75, 40, 163, 255] },
  4: { name: "other corruption", rgba: [81, 28, 63, 255] },
};

const toCssColor = ([red, green, blue, alpha]: Rgba) =>
  `rgba(${red}, ${green}, ${blue}, ${alpha / 255})`;

// The backend sends class names (not ids) in regional_class_share, so colors are looked up by name.
export const damageClassColorByName: Record<string, string> = Object.fromEntries(
  Object.values(ROAD_DAMAGE_CLASSES).map(({ name, rgba }) => [name, toCssColor(rgba)]),
);