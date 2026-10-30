import type { FullConfig } from '@nekosu/maa-tools'

const config: FullConfig = {
  cwd: import.meta.dirname,
  maaVersion: 'latest',
  interfacePath: 'assets/interface.json',
  check: {
    override: {
      // 一期模板图还没从 MuMu 裁进来，路径写在 pipeline 里，文件故意不提交。
      // 裁图落地后删掉这条，否则写错文件名也不会再报错。
      // Phase-1 crops are not in git yet. Remove this once the PNGs exist.
      'unknown-image': 'ignore'
    }
  }
}

export default config
