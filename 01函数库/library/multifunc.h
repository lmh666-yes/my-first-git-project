#ifndef MULTIFUNC_H
#define MULTIFUNC_H

#include <stdbool.h>

// 函数指针类型：所有被管理的函数都必须符合此签名
typedef int (*func_t)(void *arg);

// 功能描述结构体
typedef struct {
    const char *name;           // 功能名称
    func_t func;                // 函数指针
    void *arg;                  // 参数（可为 NULL）
    bool mandatory;             // 是否必须成功（失败则终止）
} FuncStep;

// 执行器结构体
typedef struct {
    FuncStep *steps;            // 步骤数组
    int step_count;             // 总步骤数
    int current_step;           // 当前执行步骤索引（用于调试/恢复）
    bool stop_on_error;         // 遇到错误是否停止
    void (*on_error)(int code); // 错误回调
} MultiFuncExecutor;

// ===== 创建执行器 =====
MultiFuncExecutor* executor_create(FuncStep steps[], int count, bool stop_on_error);

// ===== 执行所有步骤 =====
int executor_run(MultiFuncExecutor *exec);

// ===== 链式调用：添加步骤（方便动态构建） =====
MultiFuncExecutor* executor_add_step(MultiFuncExecutor *exec, const char *name, func_t func, void *arg, bool mandatory);

// ===== 设置错误回调 =====
void executor_set_error_callback(MultiFuncExecutor *exec, void (*cb)(int));

// ===== 获取当前执行状态 =====
int executor_get_last_error(MultiFuncExecutor *exec);

// ===== 释放执行器 =====
void executor_free(MultiFuncExecutor *exec);

#endif // MULTIFUNC_H