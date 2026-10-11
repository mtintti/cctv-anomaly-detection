import { damageClassColorByName } from "./damage_classnames-colors";

export interface MapScores {
  map: number;
  map_50: number;
  map_75: number;
}

interface ReferenceScores {
  annotation_id: number;
  updated_at: string;
  bbox: MapScores;
  segm: MapScores;
}

export interface ProxyMetrics {
  same_camera_found: boolean;
  reference_count: number;
  per_reference: ReferenceScores[];
  regional_class_share: Record<string, number>;
  regional_annotation_count: number;
  bbox: MapScores;
  segm: MapScores;
}

const MAP_BAR_COLOR = "rgb(100 116 139)";
const UNKNOWN_CLASS_COLOR = MAP_BAR_COLOR;

function MeterRow({ label, valueText, fraction, color, showSwatch = false }: {
  label: string;
  valueText: string;
  fraction: number;
  color: string;
  showSwatch?: boolean;
}) {
  return (
    <div className="flex flex-col gap-1">
      <div className="flex items-baseline justify-between gap-1 text-sm">
        <span className="flex items-center gap-2 first-letter:uppercase">
          {showSwatch && <span className="h-2.5 w-2.5 shrink-0 rounded-full" style={{ backgroundColor: color }} />}
          {label}
        </span>
        <span>{valueText}</span>
      </div>
      <div
        role="meter"
        aria-label={label}
        aria-valuemin={0}
        aria-valuemax={1}
        aria-valuenow={fraction}
        className="h-1 rounded-full bg-gray-300"
      >
        <div className="h-full rounded-full" style={{ width: `${fraction * 100}%`, backgroundColor: color }} />
      </div>
    </div>
  );
}

function MapScoreCard({ title, scores }: { title: string; scores: MapScores }) {
  return (
    <section className="flex flex-col gap-1 rounded-md bg-gray-200/70 p-2 font-light text-slate-700 inset-shadow-sm inset-shadow-gray-300">
      <header>
        <h3 className="text-lg">{title} vs prediction</h3>
        <p className="text-xs text-slate-600">mAP (intersection) averaged over time</p>
        <p className="text-xs text-slate-600">for the whole image and camera's angle</p>
      </header>
      <p className="text-3xl">{scores.map.toFixed(3)}</p>
      <MeterRow label="mAP @ IoU 0.50" valueText={scores.map_50.toFixed(3)} fraction={scores.map_50} color={MAP_BAR_COLOR} />
      <MeterRow label="mAP @ IoU 0.75" valueText={scores.map_75.toFixed(3)} fraction={scores.map_75} color={MAP_BAR_COLOR} />
    </section>
  );
}


function RegionalClassShareCard({ classShare, annotationCount, proxyMetrics }: {
  classShare: Record<string, number>;
  annotationCount: number;
}) {
  const sharesLargestFirst = Object.entries(classShare).sort(([, shareA], [, shareB]) => shareB - shareA);

  return (
    <section className="flex flex-col gap-2 rounded-md bg-gray-300 p-4 font-light text-slate-700 inset-shadow-sm inset-shadow-gray-400/50 @md:col-span-2">
      <header>
        <h3 className="text-lg">Regional class share</h3>
        <p className="text-xs text-slate-600">Damage types across {annotationCount} annotations in this cameras location across all angles</p>
      </header>
      {sharesLargestFirst.map(([className, share]) => (
        <MeterRow
          key={className}
          label={className}
          valueText={`${Math.round(share * annotationCount)} of ${annotationCount}  ${(share * 100).toFixed(1)}%`}
          fraction={share}
          color={damageClassColorByName[className] ?? UNKNOWN_CLASS_COLOR}
          showSwatch
        />
      ))}

    </section>
  );
}


export default function ProxyMetricsCards({ proxyMetrics }: { proxyMetrics?: ProxyMetrics }) {
  if (!proxyMetrics) return  <div className="flex h-full w-full items-center justify-center bg-gray-200 gap-2">
      <img src="https://images.unsplash.com/vector-1773327306991-a1e4d5ad75ad?q=80&w=580&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=NHwxMjA3fDA%3D" alt="proxy metrics were not created" width="40" height="40"/>
      <p className="text-center">ml mAP metrics are not found</p>
    </div>;

  return (
    <div className="@container">
      <div className="grid grid-cols-1 gap-1 @md:grid-cols-2">
        <MapScoreCard title="Bounding box" scores={proxyMetrics.bbox} />
        <MapScoreCard title="Segmentation mask" scores={proxyMetrics.segm} />
        <RegionalClassShareCard
          classShare={proxyMetrics.regional_class_share}
          annotationCount={proxyMetrics.regional_annotation_count}
          proxyMetrics={proxyMetrics}
        />
      </div>
    </div>
  );
}