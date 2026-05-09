import { Button } from "./ui/button";
import { ReactNode } from "react";

type Props = {
  title: string;
  children: ReactNode;
  link: string;
  className?: string;
};
export function OfferSection({ title, children, link, className }: Props) {
  return (
    <section className={className}>
      <div className="mb-2 flex items-center justify-between">
        <div className="text-md font-semibold">{title}</div>
        <a href={link}>
          <Button variant="link">مشاهده همه</Button>
        </a>
      </div>
      <div className="grid grid-cols-2 gap-2 md:grid-cols-4 md:gap-4">
        {children}
      </div>
    </section>
  );
}
