import { Link, Outlet, useNavigate } from "react-router";
import { LogOut, MapPin, ShoppingCart, Store, User } from "lucide-react";
import { removeTokens, useAuth } from "@/hooks/useAuth";

import Container from "@/components/ui/container";
import Footer from "../components/footer";
import Header from "../components/header";
import { Loading } from "@/components/loading";
import { ServerError } from "@/components/serverError";
import { Toaster } from "@/components/ui/sonner";
import { useEffect } from "react";
import { useUserInfo } from "@/api/myuser/myuser.hooks";

export default function ProfileLayout() {
  const { data, isLoading, isError } = useUserInfo();
  const navigate = useNavigate();
  const { isLogin } = useAuth();
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
    <>
      <Header />
      <Container>
        <div className="flex flex-row gap-2">
          <div className="w-[300px] shrink-0 grow-0">
            <div className="rounded-2xl border px-4 py-6">
              <ul className="flex flex-col *:border-b">
                <li>
                  <Link
                    className="flex items-center gap-1.5 py-3"
                    to="/profile"
                  >
                    <User />
                    مشخصات
                  </Link>
                </li>
                <li>
                  <Link
                    className="flex items-center gap-1.5 py-3"
                    to="/profile/orders"
                  >
                    <ShoppingCart />
                    سفارش ها
                  </Link>
                </li>
                <li>
                  <Link
                    className="flex items-center gap-1.5 py-3"
                    to="/profile/address"
                  >
                    <MapPin />
                    آدرس ها
                  </Link>
                </li>
                <li>
                  <Link
                    className="flex items-center gap-1.5 py-3"
                    to={data?.is_seller ? "/store-admin" : "/profile/my-store"}
                  >
                    <Store />
                    فروشگاه
                  </Link>
                </li>
                <li>
                  <Link
                    onClick={(e) => {
                      e.preventDefault();
                      removeTokens();
                      navigate("/");
                    }}
                    className="flex items-center gap-1.5 py-3"
                    to="#"
                  >
                    <LogOut />
                    خروج
                  </Link>
                </li>
              </ul>
            </div>
          </div>
          <div className="grow">
            <Outlet />
          </div>
        </div>
      </Container>
      <Toaster position="top-center" />
      <Footer />
    </>
  );
}
