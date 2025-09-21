module.exports = {
  testEnvironment: 'jsdom',
  transform: { '^.+\\.(ts|tsx)$': ['ts-jest', { tsconfig: 'tsconfig.json' }] },
  setupFilesAfterEnv: ['<rootDir>/jest.setup.ts']
};
