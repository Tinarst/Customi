import { AddAddress } from "./_components/add-address";
import { AddressBox } from "./_components/address-box";
import { Button } from "@/components/ui/button";
import { Loading } from "@/components/loading";
import { Plus } from "lucide-react";
import { ServerError } from "@/components/serverError";
import { useUserAddress } from "@/api/myuser/myuser.hooks";

export default function Address() {
  const { data: addresses, isLoading, isError } = useUserAddress();
  if (isLoading) return <Loading />;
  if (isError) return <ServerError />;
  return (
    <div className="rounded-2xl border px-4 pt-6">
      <div className="mb-4 flex items-center justify-between">
        <div className="border-primary border-b-2 pb-2">آدرس ها</div>
        <AddAddress
          renderButton={(setOpen) => (
            <Button onClick={() => setOpen(true)}>
              <Plus />
              اضافه کردن آدرس
            </Button>
          )}
        />
      </div>
      <ul className="flex flex-col gap-2 px-2 py-4">
        {addresses?.map((address) => (
          <AddressBox showOption key={address.id} address={address} />
        ))}
      </ul>
    </div>
  );
}
