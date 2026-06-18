import { Box, Download, Store } from "lucide-react";

import { Button } from "@/components/ui/button";

const gates = [
  {
    icon: Box,
    label: "3D 预览后续开放",
  },
  {
    icon: Download,
    label: "生产导出后续开放",
  },
  {
    icon: Store,
    label: "市场功能后续开放",
  },
];

export function FutureGates() {
  return (
    <div aria-label="未来能力" className="grid gap-2">
      {gates.map((gate) => {
        const Icon = gate.icon;

        return (
          <Button
            aria-disabled="true"
            aria-label={gate.label}
            className="w-full justify-start"
            disabled
            key={gate.label}
            title={gate.label}
            type="button"
            variant="outline"
          >
            <Icon aria-hidden="true" className="h-4 w-4" />
            {gate.label}
          </Button>
        );
      })}
    </div>
  );
}
