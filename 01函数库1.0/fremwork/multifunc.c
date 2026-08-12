#include "multifunc.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// 错误码定义
#define EXEC_OK          0
#define EXEC_ERR_STEP   -1
#define EXEC_ERR_MEM    -2
#define EXEC_ERR_CANCEL -3

MultiFuncExecutor* executor_create(FuncStep steps[], int count, bool stop_on_error) {
    MultiFuncExecutor *exec = (MultiFuncExecutor*)malloc(sizeof(MultiFuncExecutor));
    if (!exec) return NULL;

    exec->steps = (FuncStep*)malloc(count * sizeof(FuncStep));
    if (!exec->steps) {
        free(exec);
        return NULL;
    }

    memcpy(exec->steps, steps, count * sizeof(FuncStep));
    exec->step_count = count;
    exec->current_step = 0;
    exec->stop_on_error = stop_on_error;
    exec->on_error = NULL;

    return exec;
}

int executor_run(MultiFuncExecutor *exec) {
    if (!exec) return EXEC_ERR_MEM;

    int err_code = EXEC_OK;

    for (int i = 0; i < exec->step_count; i++) {
        exec->current_step = i;
        FuncStep *step = &exec->steps[i];

        printf("[执行] %s ... ", step->name);

        int ret = step->func(step->arg);

        if (ret != 0) {
            printf("❌ 失败 (code=%d)\n", ret);
            if (step->mandatory) {
                if (exec->on_error) exec->on_error(ret);
                if (exec->stop_on_error) {
                    err_code = EXEC_ERR_STEP;
                    break;
                }
            }
        } else {
            printf("✅ 成功\n");
        }
    }

    printf("\n[执行完毕] 总步骤: %d, 最终状态: %s\n", 
           exec->step_count, 
           err_code == EXEC_OK ? "✅ 全部成功" : "❌ 有步骤失败");

    return err_code;
}

MultiFuncExecutor* executor_add_step(MultiFuncExecutor *exec, const char *name, func_t func, void *arg, bool mandatory) {
    if (!exec) return NULL;

    int new_count = exec->step_count + 1;
    FuncStep *new_steps = (FuncStep*)realloc(exec->steps, new_count * sizeof(FuncStep));
    if (!new_steps) return NULL;

    exec->steps = new_steps;
    exec->step_count = new_count;

    exec->steps[new_count - 1].name = name;
    exec->steps[new_count - 1].func = func;
    exec->steps[new_count - 1].arg = arg;
    exec->steps[new_count - 1].mandatory = mandatory;

    return exec;
}

void executor_set_error_callback(MultiFuncExecutor *exec, void (*cb)(int)) {
    if (exec) exec->on_error = cb;
}

int executor_get_last_error(MultiFuncExecutor *exec) {
    return exec ? exec->current_step : -1;
}

void executor_free(MultiFuncExecutor *exec) {
    if (exec) {
        free(exec->steps);
        free(exec);
    }
}