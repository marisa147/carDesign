import * as React from "react";

import { cn } from "@/lib/utils";

function Alert({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "rounded-lg border border-border bg-card px-4 py-3 text-sm text-foreground",
        className,
      )}
      role="alert"
      {...props}
    />
  );
}

function AlertTitle({
  className,
  ...props
}: React.HTMLAttributes<HTMLHeadingElement>) {
  return (
    <h4 className={cn("font-semibold leading-[1.5]", className)} {...props} />
  );
}

function AlertDescription({
  className,
  ...props
}: React.HTMLAttributes<HTMLParagraphElement>) {
  return (
    <p className={cn("mt-1 text-secondary-foreground", className)} {...props} />
  );
}

export { Alert, AlertDescription, AlertTitle };
