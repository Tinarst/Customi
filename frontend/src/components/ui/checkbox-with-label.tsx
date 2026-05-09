import { InputHTMLAttributes } from "react";

interface CheckboxWithLabelProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  id: string;
  error?: string;
  className?: string;
}

const CheckboxWithLabel: React.FC<CheckboxWithLabelProps> = ({
  label,
  id,
  error,
  className,
  ...props
}) => {
  return (
    <div className={`flex flex-col gap-1 ${className ?? ""}`}>
      <label htmlFor={id} className="flex cursor-pointer items-center gap-2">
        <input type="checkbox" id={id} className="h-4 w-4" {...props} />
        <span>{label}</span>
      </label>

      {error && <span className="text-sm text-red-500">{error}</span>}
    </div>
  );
};

export default CheckboxWithLabel;
