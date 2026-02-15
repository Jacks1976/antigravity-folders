/**
 * Validation utilities for form inputs
 */

export interface ValidationError {
  field: string;
  message: string;
}

export const validateEmail = (email: string): string | null => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  
  if (!email) {
    return 'Email é obrigatório';
  }
  
  if (!emailRegex.test(email)) {
    return 'Email inválido';
  }
  
  return null;
};

export const validatePassword = (password: string): string[] => {
  const errors: string[] = [];
  
  if (!password) {
    return ['Senha é obrigatória'];
  }
  
  if (password.length < 12) {
    errors.push('Mínimo de 12 caracteres');
  }
  
  if (!/[a-z]/.test(password)) {
    errors.push('Precisa de letras minúsculas');
  }
  
  if (!/[A-Z]/.test(password)) {
    errors.push('Precisa de letras maiúsculas');
  }
  
  if (!/\d/.test(password)) {
    errors.push('Precisa de números');
  }
  
  if (!/[!@#$%^&*]/.test(password)) {
    errors.push('Precisa de símbolos (!@#$%^&*)');
  }
  
  return errors;
};

export const validatePasswordMatch = (password: string, confirm: string): string | null => {
  if (password !== confirm) {
    return 'As senhas não correspondem';
  }
  return null;
};

export const validateFullName = (name: string): string | null => {
  if (!name) {
    return 'Nome é obrigatório';
  }
  
  if (name.trim().length < 3) {
    return 'Nome deve ter pelo menos 3 caracteres';
  }
  
  // Check if has at least 2 words
  if (name.trim().split(/\s+/).length < 2) {
    return 'Informe seu nome completo';
  }
  
  return null;
};

export const validateForm = (formData: {
  email: string;
  fullName?: string;
  password: string;
  confirmPassword?: string;
}): ValidationError[] => {
  const errors: ValidationError[] = [];
  
  const emailError = validateEmail(formData.email);
  if (emailError) {
    errors.push({ field: 'email', message: emailError });
  }
  
  if (formData.fullName !== undefined) {
    const nameError = validateFullName(formData.fullName);
    if (nameError) {
      errors.push({ field: 'fullName', message: nameError });
    }
  }
  
  const passwordErrors = validatePassword(formData.password);
  if (passwordErrors.length > 0) {
    errors.push({ field: 'password', message: passwordErrors.join(', ') });
  }
  
  if (formData.confirmPassword !== undefined) {
    const matchError = validatePasswordMatch(formData.password, formData.confirmPassword);
    if (matchError) {
      errors.push({ field: 'confirmPassword', message: matchError });
    }
  }
  
  return errors;
};
