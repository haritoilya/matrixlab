// Скачивает файлы, которые не вошли в выгрузку конструктора Т-Банка
// (PDF с документами и шрифт DINPro). Запуск из корня проекта:
//   node scripts/fetch-assets.mjs
// Нужен Node.js 18 или новее. Скачать нужно ДО 1 декабря, пока хранилище конструктора доступно.
import { mkdir, writeFile, stat } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const ITEMS = [
  {
    "dest": "assets/fonts/DINPro-CondensedBold.eot",
    "url": "https://s.tb.ru/fonts/dinpro/DINPro-CondensedBold.eot"
  },
  {
    "dest": "assets/fonts/DINPro-CondensedBold.ttf",
    "url": "https://s.tb.ru/fonts/dinpro/DINPro-CondensedBold.ttf"
  },
  {
    "dest": "assets/fonts/DINPro-CondensedBold.woff",
    "url": "https://s.tb.ru/fonts/dinpro/DINPro-CondensedBold.woff"
  },
  {
    "dest": "assets/fonts/DINPro-CondensedBold.woff2",
    "url": "https://s.tb.ru/fonts/dinpro/DINPro-CondensedBold.woff2"
  },
  {
    "dest": "files/buklet-partner.pdf",
    "url": "https://90f1661d-2ff4-4f29-b07c-0e47453ca691.selstorage.ru/site684476%2F%D0%91%D1%83%D0%BA%D0%BB%D0%B5%D1%82%5F%D0%9F%D0%B0%D1%80%D1%82%D0%BD%D0%B5%D1%80%2Epdf"
  },
  {
    "dest": "files/elastin-klin-issled-statya-1.pdf",
    "url": "https://90f1661d-2ff4-4f29-b07c-0e47453ca691.selstorage.ru/site684476%2F%D0%AD%D0%BB%D0%B0%D1%81%D1%82%D0%B8%D0%BD%5F%D0%9A%D0%BB%D0%B8%D0%BD%5F%D0%98%D1%81%D1%81%D0%BB%D0%B5%D0%B4%5F%D0%A1%D1%82%D0%B0%D1%82%D1%8C%D1%8F%5F1%2Epdf"
  },
  {
    "dest": "files/elastin-klin-issled-statya-2.pdf",
    "url": "https://90f1661d-2ff4-4f29-b07c-0e47453ca691.selstorage.ru/site684476%2F%D0%AD%D0%BB%D0%B0%D1%81%D1%82%D0%B8%D0%BD%5F%D0%9A%D0%BB%D0%B8%D0%BD%5F%D0%98%D1%81%D1%81%D0%BB%D0%B5%D0%B4%5F%D0%A1%D1%82%D0%B0%D1%82%D1%8C%D1%8F%5F2%2Epdf"
  },
  {
    "dest": "files/sertifikat-2-stranicy-20221027.pdf",
    "url": "https://90f1661d-2ff4-4f29-b07c-0e47453ca691.selstorage.ru/site684476%2F%D0%A1%D0%B5%D1%80%D1%82%D0%B8%D1%84%D0%B8%D0%BA%D0%B0%D1%82%202%20%D1%81%D1%82%D1%80%D0%B0%D0%BD%D0%B8%D1%86%D1%8B%5F20221027%2Epdf"
  },
  {
    "dest": "files/sertifikat-sootvetstviya-dobrovolnyj-bad.pdf",
    "url": "https://90f1661d-2ff4-4f29-b07c-0e47453ca691.selstorage.ru/site684476%2F%D0%A1%D0%B5%D1%80%D1%82%D0%B8%D1%84%D0%B8%D0%BA%D0%B0%D1%82%5F%D1%81%D0%BE%D0%BE%D1%82%D0%B2%D0%B5%D1%82%D1%81%D1%82%D0%B2%D0%B8%D1%8F%5F%D0%B4%D0%BE%D0%B1%D1%80%D0%BE%D0%B2%D0%BE%D0%BB%D1%8C%D0%BD%D1%8B%D0%B9%5F%D0%91%D0%90%2Epdf"
  }
];

let ok = 0, fail = 0;
for (const { dest, url } of ITEMS) {
  const target = join(root, dest);
  try {
    try { await stat(target); console.log('уже есть  ', dest); ok++; continue; } catch {}
    const res = await fetch(url);
    if (!res.ok) throw new Error('HTTP ' + res.status);
    const buf = Buffer.from(await res.arrayBuffer());
    await mkdir(dirname(target), { recursive: true });
    await writeFile(target, buf);
    console.log('скачано   ', dest, '(' + buf.length + ' байт)');
    ok++;
  } catch (e) {
    console.log('ОШИБКА    ', dest, '-', e.message);
    fail++;
  }
}
console.log(`\nГотово: ${ok} из ${ITEMS.length}` + (fail ? `, не скачано: ${fail}` : ''));
process.exit(fail ? 1 : 0);
