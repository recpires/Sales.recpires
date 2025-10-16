import { useEffect, useState } from 'react';
import i18n from '../../i18n';

const LANG_KEY = 'locale';

const LanguageSelector = () => {
  const [lang, setLang] = useState<string>(() => {
    try {
      const saved = localStorage.getItem(LANG_KEY);
      return saved || i18n.language || 'pt-BR';
    } catch {
      return i18n.language || 'pt-BR';
    }
  });

  useEffect(() => {
    if (lang && i18n.language !== lang) {
      i18n.changeLanguage(lang);
    }
  }, [lang]);

  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const v = e.target.value;
    setLang(v);
    try {
      localStorage.setItem(LANG_KEY, v);
    } catch {}
    i18n.changeLanguage(v);
  };

  return (
    <select
      value={lang}
      onChange={handleChange}
      className="border border-gray-200 rounded-md px-2 py-1 text-sm bg-white"
      aria-label="Select language"
    >
      <option value="pt-BR">Português (BR)</option>
      <option value="en">English</option>
    </select>
  );
};

export default LanguageSelector;
