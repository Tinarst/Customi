import { CartEmptyState } from "./_components/cart-empty-state";
import { CartSummery } from "./_components/cart-summery";
import Container from "@/components/ui/container";
import { Loading } from "@/components/loading";
import { ProductCartItem } from "./_components/product-cart-item";
import { ServerError } from "@/components/serverError";
import { useAuth } from "@/hooks/useAuth";
import { useCart } from "@/api/mycart/mycart.hooks";
import { useEffect } from "react";
import { useNavigate } from "react-router";

export default function Cart() {
  const { data, isError, isLoading } = useCart();
  const { isLogin } = useAuth();
  const navigate = useNavigate();
  useEffect(() => {
    if (!isLogin) {
      navigate("/");
    }
  }, [isLogin, navigate]);
  if (isLoading) {
    return <Loading />;
  }
  if (isError) {
    return <ServerError />;
  }

  return (
    <Container>
      <div className="flex w-full flex-col md:flex-row">
        <div className="grow">
          <div className="border-b pb-1.5">سبد خرید</div>
          {data && data.items.length === 0 && <CartEmptyState />}
          {data?.items.map((item) => (
            <ProductCartItem key={item.id} cartItem={item} />
          ))}
        </div>
        <div>
          <CartSummery onClick={() => navigate("/checkout/shipping")} />
        </div>
      </div>
    </Container>
  );
}
