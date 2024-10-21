import { defineConfig, loadEnv } from 'vite';

import commonjs from 'vite-plugin-commonjs';
import dynamicImport from 'vite-plugin-dynamic-import';
import path from 'path';
import react from '@vitejs/plugin-react';

export default defineConfig(() => {
  return {
    build: {
      outDir: 'build',
    },
    assetsInclude: ['**/*.hdr'],
    optimizeDeps: {
      // This is required to load the .hdr files using the dev server.
      esbuildOptions: {
        loader: {
          '.hdr': 'dataurl'
        }
      }
    },
    plugins: [
      dynamicImport({
        filter(id) {
          // `node_modules` is exclude by default, so we need to include it explicitly
          // https://github.com/vite-plugin/vite-plugin-dynamic-import/blob/v1.3.0/src/index.ts#L133-L135
          if (id.includes('/node_modules/@iot-app-kit/charts-core')) {
            console.log('dynamically import entry point', id);
            return true;
          }
        },
        onFiles(files) {
          console.log('dynamically import files', files);
        }
      }),
      // required to support the commonjs require in dev builds
      commonjs(),
      react(
      {
        babel: {
          babelrc: true,
        }
      }
      ),
    ],
    server: {
      port: 3001,
      host: true
    },
    resolve: {
      alias: {
        '~': path.resolve(__dirname, 'src'),
      }
    },
    define: {
        global: {},
        'process.env': loadEnv('mock', process.cwd(), '')
    }
  };
});