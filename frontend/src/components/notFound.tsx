export function NotFound() {
  return (
    <section className="flex items-center p-16 dark:bg-gray-700">
      <div className="!max-w-[100vw] container flex flex-col items-center">
        <div className="flex max-w-md flex-col gap-6 text-center">
          <h2 className="text-9xl font-extrabold text-gray-600 dark:text-gray-100">
            <span className="sr-only">Error</span>404
          </h2>
          <p className="text-2xl md:text-2xl dark:text-gray-300">
            متاسفانه صفحه موردنظر شما یافت نشد
          </p>
          <a
            href="/"
            className="rounded-md bg-[#a73b40] px-4 py-2 hover:bg-[#902f33] px-8 py-4 text-xl font-semibold text-gray-50 hover:text-gray-200"
          >
            بازگشت به خانه
          </a>
        </div>
      </div>
    </section>
  );
}
