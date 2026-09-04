import { Folder, Boxes } from "lucide-react";

interface QuickLink {
  label: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  tone: "light" | "dark";
}

const LINKS: QuickLink[] = [
  { label: "datasets", href: "/dashboard/datasets", icon: Folder, tone: "light" },
  { label: "models", href: "/dashboard/models", icon: Boxes, tone: "dark" },
];

export default function FilesModelsCard() {
  return (
    <section
      aria-label="Quick access"
      className="rounded-2xl bg-gradient-to-br from-neutral-300 via-neutral-200 to-neutral-300 p-6"
    >
      <div className="flex flex-wrap gap-4">
        {LINKS.map(({ label, href, icon: Icon, tone }) => (
          <a
            key={href}
            href={href}
            className="flex items-center gap-3 rounded-xl bg-white/90 px-5 py-4 text-sm font-medium text-neutral-800 shadow-sm transition-transform hover:-translate-y-0.5 hover:shadow-md"
          >
            <span
              className={`flex h-8 w-8 items-center justify-center rounded-md ${
                tone === "dark" ? "bg-neutral-500" : "bg-neutral-200"
              }`}
            >
              <Icon className={`h-4 w-4 ${tone === "dark" ? "text-white" : "text-neutral-600"}`} />
            </span>
            {label}
          </a>
        ))}
      </div>
    </section>
  );
}