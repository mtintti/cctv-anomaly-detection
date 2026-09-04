export interface ProjectSummary {
  id: string;
  name: string;
  colorHex: string;
}

interface ProjectsCardProps {
  projects?: ProjectSummary[];
}

export default function ProjectsJoined({ projects = [] }: ProjectsCardProps) {
  return (
    <section aria-label="Projects you belong to" className="rounded-2xl bg-neutral-100 p-6">
      <h2 className="text-sm font-medium text-neutral-500">Projects you belong to</h2>

      {projects.length === 0 ? (
        <p className="mt-4 text-sm text-neutral-400">You haven&apos;t joined any shared projects yet.</p>
      ) : (
        <ul className="mt-4 flex flex-wrap gap-4">
          {projects.map((project) => (
            <li key={project.id} className="flex items-center gap-2 text-sm text-neutral-700">
              <span className="h-3 w-3 rounded-full" style={{ backgroundColor: project.colorHex }} aria-hidden />
              {project.name}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}