<template>
	<!--编辑新增界面-->
    <el-dialog :title="editFormTitle" :visible.sync="dialogShow" @close="$emit('close')" 
               :close-on-click-modal="false">
        <el-form ref="editForm" :model="editForm" :rules="rules" label-width="80px">
            <el-form-item prop="db_user" label="账号">
                <el-input v-model="editForm.db_user" auto-complete="off" :disabled="is_disabled"></el-input>
            </el-form-item>
            <el-form-item prop="db_password" label="密码">
                <el-input v-model="editForm.db_password" auto-complete="off" :disabled="is_disabled"></el-input>
            </el-form-item>
            <el-form-item prop="db_database" label="数据库">
            <el-select
                v-model="db_databases"
                multiple
                filterable
                allow-create
                default-first-option
                placeholder="请选择数据库">
                <el-option
                  v-for="item in options5"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value">
                </el-option>
            </el-select>
            </el-form-item>
            <el-alert v-if="error" :title="error" type="error" style="margin-top: -10px; margin-bottom: 10px"
                      show-icon></el-alert>
        </el-form>
        <div slot="footer">
            <el-button type="text" @click.native="dialogShow = false">取消</el-button>
            <el-button type="primary" :loading="editLoading" @click.native="editSubmit">保存</el-button>
        </div>
    </el-dialog>
</template>

<style>

</style>

<script>
    export default {
        data () {
            return {
                editFormTitle: '',
                dialogShow: true,
                editForm: {
                    'db_user':'',
                    'db_password':''
                },
                rules: {
                    db_user: [
                        {required: true, message: '请输入账号', trigger: 'blur'}
                    ],
                    db_password: [
                        {required: true, message: '请输入密码', trigger: 'blur'}
                    ],
                },
                editLoading: false,
                is_disabled: false,
                error: false
            }
        },
        mothods: {
            editSubmit: function () {
                this.$refs.editForm.validate((valid) => {
                    if (valid) {
                        this.editLoading = true;
                        this.error = '';
                        this.dialogShow = false;
                        if (this.editForm.id) {
                            this.$http.put(`/api/account/users/${this.editForm.id}`, this.editForm).then(this.resp,
                                response => this.$layer_message(response.result)).finally(() => this.editLoading = false)
                        } else {
                            this.$http.post('/api/account/users/', this.editForm).then(this.resp,
                                response => this.$layer_message(response.result)).finally(() => this.editLoading = false)
                        }
                    }
                });
            }
        }

    }
</script>
