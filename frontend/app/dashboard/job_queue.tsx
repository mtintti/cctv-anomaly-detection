export interface Job {
  id: string;
  label: string;
  progress: number; // 0-100
}

interface JobQueueCardProps {
  jobs?: Job[];
}


export default function JobQueueCard({ jobs = [] }: JobQueueCardProps) {
  return (
    <section aria-label="Job queue" className="flex min-h-[220px] flex-col rounded-2xl bg-neutral-100 p-6">
      <h2 className="text-sm font-medium text-neutral-500">Job queue</h2>

      {jobs.length === 0 ? (
        <div className="flex flex-1 items-center justify-center text-center text-lg font-medium text-neutral-400">
          Job queue empty
        </div>
      ) : (
        <ul className="mt-4 flex flex-col gap-3">
          {jobs.map((job) => (
            <li key={job.id} className="text-sm text-neutral-700">
              <div className="flex justify-between">
                <span>{job.label}</span>
                <span>{job.progress}%</span>
              </div>
              <div className="mt-1 h-1.5 w-full overflow-hidden rounded-full bg-neutral-200">
                <div className="h-full rounded-full bg-neutral-500" style={{ width: `${job.progress}%` }} />
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}