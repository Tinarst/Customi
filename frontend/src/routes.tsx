import { BrowserRouter, Route, Routes } from "react-router";

import { lazy } from "react";
import withSuspense from "./components/withSuspend";

const Layout = withSuspense(lazy(() => import("./components/layouts/site")));
const StoreLayout = withSuspense(
  lazy(() => import("./components/layouts/store")),
);
const ProfileLayout = withSuspense(
  lazy(() => import("./components/layouts/profile/layout")),
);

const Home = withSuspense(lazy(() => import("./pages/Home")));
const Login = withSuspense(lazy(() => import("./pages/auth/login")));
const Register = withSuspense(lazy(() => import("./pages/auth/register")));
const Category = withSuspense(
  lazy(() => import("./pages/categories/category")),
);
const ShowAllNew = withSuspense(
  lazy(() => import("./pages/show-all-new/show")),
);
const ShowAllRate = withSuspense(
  lazy(() => import("./pages/show-all-rate/show")),
);
const Cart = withSuspense(lazy(() => import("./pages/checkout/cart")));
const Shipping = withSuspense(lazy(() => import("./pages/checkout/shipping")));
const Product = withSuspense(lazy(() => import("./pages/products/product")));
const Profile = withSuspense(lazy(() => import("./pages/profile/profile")));
const Address = withSuspense(lazy(() => import("./pages/profile/address")));
const Orders = withSuspense(lazy(() => import("./pages/profile/orders")));
const Order = withSuspense(lazy(() => import("./pages/profile/order")));
const Store = withSuspense(lazy(() => import("./pages/store/store")));
const MyStoreDetails = withSuspense(
  lazy(() => import("./pages/profile/my-store")),
);
const StoreDashboard = withSuspense(
  lazy(() => import("./pages/my-store/Home")),
);
const CategoriesAdmin = withSuspense(
  lazy(() => import("./pages/my-store/categories")),
);
const ProductsAdmin = withSuspense(
  lazy(() => import("./pages/my-store/products")),
);
const StoreProducts = withSuspense(
  lazy(() => import("./pages/my-store/store-products")),
);
const OrdersAdmin = withSuspense(lazy(() => import("./pages/my-store/orders")));
const NotFound = withSuspense(lazy(() => import("./pages/NotFound")));
export default function AppRoutes() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="categories/:categoryId/" element={<Category />} />
          <Route path="show-all-new/" element={<ShowAllNew />} />
          <Route path="show-all-rate/" element={<ShowAllRate />} />
          <Route path="products/:productId/" element={<Product />} />
          <Route path="stores/:storeId/" element={<Store />} />
          <Route path="/auth">
            <Route path="login" element={<Login />} />
            <Route path="register" element={<Register />} />
          </Route>
        </Route>
        <Route path="/store-admin" element={<StoreLayout />}>
          <Route index element={<StoreDashboard />} />
          <Route path="categories" element={<CategoriesAdmin />} />
          <Route path="products" element={<ProductsAdmin />} />
          <Route path="store-products" element={<StoreProducts />} />
          <Route path="orders" element={<OrdersAdmin />} />
        </Route>
        <Route path="/profile" element={<ProfileLayout />}>
          <Route index element={<Profile />} />
          <Route path="address" element={<Address />} />
          <Route path="orders" element={<Orders />} />
          <Route path="orders/:orderId" element={<Order />} />
          <Route path="my-store" element={<MyStoreDetails />} />
        </Route>
        <Route path="/checkout" element={<Layout />}>
          <Route path="cart" element={<Cart />} />
          <Route path="shipping" element={<Shipping />} />
        </Route>
        <Route element={<Layout />}></Route>
        <Route element={<Layout />}>
          <Route path="*" element={<NotFound />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
