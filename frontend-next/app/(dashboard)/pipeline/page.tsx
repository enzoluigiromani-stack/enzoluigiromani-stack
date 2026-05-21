import { PipelineBoard } from "@/components/pipeline/pipeline-board";

export default function PipelinePage() {
  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Pipeline</h1>
        <p className="text-muted-foreground">Gerencie seu funil de vendas com drag &amp; drop</p>
      </div>
      <PipelineBoard />
    </div>
  );
}
