/**
 * Password Strength Indicator Component
 */

interface PasswordStrengthProps {
  password: string;
}

export function PasswordStrengthIndicator({ password }: PasswordStrengthProps) {
  const checks = {
    length: password.length >= 12,
    uppercase: /[A-Z]/.test(password),
    lowercase: /[a-z]/.test(password),
    number: /\d/.test(password),
    symbol: /[!@#$%^&*]/.test(password),
  };

  const passedChecks = Object.values(checks).filter(Boolean).length;
  const totalChecks = Object.keys(checks).length;
  const strength = Math.round((passedChecks / totalChecks) * 100);

  const getStrengthColor = () => {
    if (strength === 0) return 'bg-gray-300';
    if (strength < 40) return 'bg-red-500';
    if (strength < 70) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  const getStrengthText = () => {
    if (strength === 0) return 'Digite uma senha';
    if (strength < 40) return 'Fraca';
    if (strength < 70) return 'Media';
    return 'Forte';
  };

  return (
    <div className="mt-3 space-y-2">
      {/* Strength Bar */}
      <div className="flex items-center gap-2">
        <div className="flex-1 bg-gray-200 rounded-full h-2 overflow-hidden">
          <div
            className={`h-full transition-all duration-300 ${getStrengthColor()}`}
            style={{ width: `${strength}%` }}
          ></div>
        </div>
        <span className="text-xs font-semibold text-gray-700 w-12">{getStrengthText()}</span>
      </div>

      {/* Requirements Checklist */}
      <div className="text-xs space-y-1">
        <div className={`flex items-center ${checks.length ? 'text-green-600' : 'text-gray-500'}`}>
          <span className={`inline-block w-4 h-4 mr-1 rounded-sm border ${checks.length ? 'bg-green-500 border-green-600' : 'border-gray-300'}`}>
            {checks.length && <span className="text-white text-xs">✓</span>}
          </span>
          Mínimo 12 caracteres
        </div>
        <div className={`flex items-center ${checks.uppercase ? 'text-green-600' : 'text-gray-500'}`}>
          <span className={`inline-block w-4 h-4 mr-1 rounded-sm border ${checks.uppercase ? 'bg-green-500 border-green-600' : 'border-gray-300'}`}>
            {checks.uppercase && <span className="text-white text-xs">✓</span>}
          </span>
          Letras maiúsculas (A-Z)
        </div>
        <div className={`flex items-center ${checks.lowercase ? 'text-green-600' : 'text-gray-500'}`}>
          <span className={`inline-block w-4 h-4 mr-1 rounded-sm border ${checks.lowercase ? 'bg-green-500 border-green-600' : 'border-gray-300'}`}>
            {checks.lowercase && <span className="text-white text-xs">✓</span>}
          </span>
          Letras minúsculas (a-z)
        </div>
        <div className={`flex items-center ${checks.number ? 'text-green-600' : 'text-gray-500'}`}>
          <span className={`inline-block w-4 h-4 mr-1 rounded-sm border ${checks.number ? 'bg-green-500 border-green-600' : 'border-gray-300'}`}>
            {checks.number && <span className="text-white text-xs">✓</span>}
          </span>
          Números (0-9)
        </div>
        <div className={`flex items-center ${checks.symbol ? 'text-green-600' : 'text-gray-500'}`}>
          <span className={`inline-block w-4 h-4 mr-1 rounded-sm border ${checks.symbol ? 'bg-green-500 border-green-600' : 'border-gray-300'}`}>
            {checks.symbol && <span className="text-white text-xs">✓</span>}
          </span>
          Símbolos especiais (!@#$%^&*)
        </div>
      </div>
    </div>
  );
}
