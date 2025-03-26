import { defineConfig } from 'astro/config';
import react from '@astrojs/react';

// https://astro.build/config
export default defineConfig({
  integrations: [react({
    // Configuración para asegurar que todas las dependencias de React sean procesadas
    include: ['**.jsx', '**.tsx']
  })],
});