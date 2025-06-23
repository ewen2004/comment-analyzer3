<template>
  <div class="app-container">
    <header class="app-header">
      <div class="container">
        <h1 class="app-title">海内外评论分析系统</h1>
      </div>
    </header>

    <main class="app-main">
      <router-view />
    </main>

    <footer class="app-footer">
      <div class="container">
        <p>© {{ new Date().getFullYear() }} 评论分析系统</p>
      </div>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.app-header {
  background-color: white;
  padding: 15px 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.app-title {
  font-size: 24px;
  font-weight: 600;
  color: var(--primary-color);
}

.app-main {
  flex: 1;
  padding: 20px 0;
}

.app-footer {
  background-color: #f0f2f5;
  padding: 15px 0;
  text-align: center;
  font-size: 14px;
  color: #909399;
}
</style>
