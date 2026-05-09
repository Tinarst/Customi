import { Link, useNavigate } from "react-router";
import { RequestOtpPayload, RequestVerifyPayload } from "@/types";
import { useEffect, useState } from "react";
import { useRegister, useRequestOtp } from "@/api/auth/auth.hooks";

import { Button } from "@/components/ui/button";
import CheckboxWithLabel from "@/components/ui/checkbox-with-label";
import InputWithLabel from "@/components/ui/input-with-label";
import { LogoTypeIcon } from "@/icons/logo-type";
import { storeTokens } from "@/hooks/useAuth";
import { useAuth } from "@/hooks/useAuth";
import { useForm } from "react-hook-form";

export default function Register() {
  const navigate = useNavigate();
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<Partial<RequestVerifyPayload>>();
  const [step, setStep] = useState<"request" | "verify">("request");
  const { isLogin } = useAuth();
  useEffect(() => {
    if (isLogin) {
      navigate("/profile");
    }
  }, [isLogin, navigate]);
  const requestVerifyOtp = useRegister({
    onSuccess(data) {
      storeTokens(data.access, data.refresh);
      navigate("/");
    },
  });
  const requestOtpMutations = useRequestOtp({
    onSuccess(data) {
      setStep("verify");
      alert(data.message);
    },
  });

  const onSubmit = async (data: Partial<RequestVerifyPayload>) => {
    if (step === "request") {
      await requestOtpMutations.mutateAsync(data as RequestOtpPayload);
    } else {
      await requestVerifyOtp.mutateAsync(data as RequestVerifyPayload);
    }
  };

  return (
    <div className="mx-auto mt-10 max-w-sm p-2">
      <a href="/">
        <LogoTypeIcon className="h-16 w-full" />
      </a>
      <p className="my-10 text-center">ثبت نام</p>

      {requestOtpMutations.isError && (
        <div className="mb-4 rounded-md bg-red-200 p-2 text-sm text-red-900">
          {requestOtpMutations.error?.response?.data?.detail ??
            requestOtpMutations.error?.message}
        </div>
      )}

      <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4">
        <InputWithLabel
          className="w-full"
          label="شماره موبایل"
          id="username"
          {...register("username", { required: "شماره موبایل الزامی است" })}
          error={errors.username?.message}
        />
        <CheckboxWithLabel
          id="userType"
          label="بعنوان فروشنده ثبت‌نام می‌کنم"
          {...register("userType")}
        />
        {step === "verify" && (
          <>
            <InputWithLabel
              type="password"
              label="کد تایید"
              id="password"
              {...register("password", { required: "کد تایید الزامی است" })}
              error={errors.password?.message}
            />
          </>
        )}
        <p className="my-6 text-center text-xs">
          عضویت شما به منزله پذیرفتن قوانین و مقررات می باشد.
        </p>
        <Button
          type="submit"
          className="w-full"
          variant="default"
          disabled={requestOtpMutations.isPending}
        >
          ثبت‌نام در سایت
        </Button>
      </form>

      <Button className="mt-6 w-full" variant="link" asChild>
        <Link to="/auth/login">ورود به سایت</Link>
      </Button>
    </div>
  );
}
