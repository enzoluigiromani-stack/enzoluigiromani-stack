function CardSkeleton() {
  return (
    <div className="bg-card border border-border rounded-xl p-3 pl-[14px] space-y-2.5 animate-pulse">
      <div className="flex items-start gap-2">
        <div className="flex-1 space-y-1.5">
          <div className="h-3.5 bg-muted rounded-md w-4/5" />
          <div className="h-2.5 bg-muted rounded-md w-2/5" />
        </div>
        <div className="h-4 w-4 bg-muted rounded" />
      </div>
      <div className="space-y-1">
        <div className="h-2.5 bg-muted rounded w-3/4" />
        <div className="h-2.5 bg-muted rounded w-1/2" />
      </div>
      <div className="flex gap-1 pt-0.5">
        <div className="h-4 w-14 bg-muted rounded-full" />
        <div className="h-4 w-10 bg-muted rounded-full" />
      </div>
    </div>
  );
}

function ColumnSkeleton({ cardCount = 3 }: { cardCount?: number }) {
  return (
    <div className="w-[272px] shrink-0">
      <div className="flex items-center gap-2 mb-3 px-1">
        <div className="h-2.5 w-2.5 rounded-full bg-muted/70 animate-pulse" />
        <div className="h-3.5 w-28 bg-muted/70 rounded animate-pulse" />
        <div className="h-4 w-6 bg-muted/70 rounded-full animate-pulse" />
      </div>
      <div className="flex flex-col gap-2 p-2 bg-muted/40 rounded-xl min-h-[420px]">
        {Array.from({ length: cardCount }).map((_, i) => (
          <CardSkeleton key={i} />
        ))}
      </div>
    </div>
  );
}

export function PipelineSkeleton() {
  return (
    <div className="space-y-5">
      {/* Header skeleton */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="h-[60px] bg-muted/50 rounded-xl animate-pulse" />
        ))}
      </div>

      {/* Board skeleton */}
      <div className="flex gap-4 overflow-x-auto pb-4">
        <ColumnSkeleton cardCount={4} />
        <ColumnSkeleton cardCount={2} />
        <ColumnSkeleton cardCount={3} />
        <ColumnSkeleton cardCount={1} />
      </div>
    </div>
  );
}
