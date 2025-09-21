export type Energy = "sustainable" | "balanced" | "intensive";
export type Model = { id: string; label: string; energy: Energy };

export const MODELS: Model[] = [
  { id: "eco-7b", label: "Eco (GreenAI-7B)", energy: "sustainable" },
  { id: "mix-13b", label: "Balanced (Mix-13B)", energy: "balanced" },
  { id: "xl-70b", label: "Performance (XL-70B)", energy: "intensive" },
    { id: "Devank", label: "Performance (XL-70B)", energy: "intensive" },

];