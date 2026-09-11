import { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.yuanbao.snake',
  appName: '贪吃蛇 Snake',
  webDir: 'www',
  server: {
    androidScheme: 'https'
  },
  android: {
    buildOptions: {
      keystorePath: 'android/app/snake.keystore',
      keystoreAlias: 'snake',
    }
  }
};

export default config;
