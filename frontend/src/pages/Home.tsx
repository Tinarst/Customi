import { CategoryCard } from "@/components/category-card";
import Container from "@/components/ui/container";
import { OfferSection } from "@/components/offer-section";
import { ProductCard } from "@/components/product-card";
import { ScrollSection } from "@/components/scroll-section";
import { useCategories } from "@/api/categories/categories.hooks";
import { useProducts } from "@/api/products/products.hooks";

export default function Home() {
  const { data: categories } = useCategories();
  const { data: newProducts } = useProducts({ ordering: "created_at" });
  const { data: mostRatedProducts } = useProducts({ ordering: "rating" });
  return (
    <main className="mb-2 md:mb-14">
      <Container>
        <OfferSection title="جدیدترین محصولات" link="/show-all-new">
          {newProducts?.results.map((item, index) => (
            <ProductCard
              key={item.id}
              className={index >= 4 ? "hidden md:block" : "block"}
              id={item.id.toString()}
              image={item.images[0]?.image}
              best_seller={item.best_seller}
              name={item.name}
            />
          ))}
        </OfferSection>
        <ScrollSection title="دسته‌بندی محصولات" className="mt-8">
          {categories?.results.map((item) => (
            <CategoryCard
              key={item.id}
              title={item.name}
              href={`/categories/${item.id}`}
              imgSrc={item.image}
            />
          ))}
        </ScrollSection>
        <OfferSection
          title="محصولات پرطرفدار"
          className="mt-6"
          link="/show-all-rate"
        >
          {mostRatedProducts?.results.map((item, index) => (
            <ProductCard
              key={item.id}
              className={index >= 4 ? "hidden md:block" : "block"}
              id={item.id.toString()}
              image={item.images[0]?.image}
              best_seller={item.best_seller}
              name={item.name}
            />
          ))}
        </OfferSection>
      </Container>
    </main>
  );
}
