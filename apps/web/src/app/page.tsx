import { WorkbenchQueryProvider } from "@/components/workbench/query-provider";
import { WorkbenchApp } from "@/components/workbench/workbench-app";

export default function Home() {
  return (
    <WorkbenchQueryProvider>
      <WorkbenchApp />
    </WorkbenchQueryProvider>
  );
}
