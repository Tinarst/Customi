import { Filter, ListFilter } from "lucide-react";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import Container from "@/components/ui/container";
import FilterForm from "@/components/modules/FilterForm";
import { PaginationControl } from "@/components/modules/pagination-control";
import { ProductCard } from "@/components/product-card";
import { ProductsQueryFilter } from "@/types";
import { useProducts } from "@/api/products/products.hooks";
import { useSiteTitle } from "@/hooks/useSiteTitle";

export default function ShowAllNew() {
  const [params, setParams] = useState<Partial<ProductsQueryFilter>>({
    ordering: "created_at",
  });
  useSiteTitle("جدیدترین‌ها");
  const { data: products } = useProducts(params);

  return (
    <Container>
      <div className="flex flex-col md:flex-row">
        <div className="bg-background sticky top-[72px] flex gap-2 border-b border-gray-300 shadow md:hidden">
          <Button variant={"ghost"}>
            <Filter />
            فیلتر
          </Button>
          <Button variant={"ghost"}>
            <ListFilter />
            پربازدیدترین
          </Button>
        </div>
        <div className="relative hidden w-[300px] shrink-0 p-2 md:block">
          <div className="sticky top-[185px]">
            <FilterForm query={params} setQuery={setParams} />
          </div>
        </div>
        <div className="w-full grow p-2">
          {products?.results.length === 0 && (
            <h2 className="text-center text-4xl font-extrabold text-gray-700">
              هیچ محصولی یافت نشد
            </h2>
          )}
          <div className="grid grow grid-cols-2 gap-2 p-2 md:grid-cols-3">
            {products?.results.map((item) => (
              <ProductCard
                key={item.id}
                id={item.id.toString()}
                image={item.images[0]?.image}
                best_seller={item.best_seller}
                name={item.name}
              />
            ))}
          </div>
          <PaginationControl
            currentPage={params?.page || 1}
            setCurrentPage={(newPage) =>
              setParams((oldParams) => ({ ...oldParams, page: newPage }))
            }
            total={products?.count}
          />
        </div>
      </div>
    </Container>
  );
}
