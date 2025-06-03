import path from 'path';
import { fileURLToPath } from 'url';
import { defineConfig } from 'vitest/config';

const currentMetaUrl = import.meta.url;
const currentFilename = fileURLToPath(currentMetaUrl);
const currentDirname = path.dirname(currentFilename);

export default defineConfig({
  test: {
    globals: true,
    environment: 'node', // Or 'jsdom' if browser APIs are needed and not heavily mocked
    include: [
      path.resolve(currentDirname, '../tests/granular/pqc_wasm_module_integrity').replace(/\\/g, '/') + '/**/*.test.ts',
      path.resolve(currentDirname, '../tests/performance').replace(/\\/g, '/') + '/**/*.test.ts',
      // Add other test paths here if needed in the future
    ],
    // Optionally, if OQS is a global that needs setup or if using jsdom:
    // setupFiles: ['./tests/setupVitest.ts'],
  },
});