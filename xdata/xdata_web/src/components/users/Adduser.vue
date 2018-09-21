<template>
	<!--编辑新增界面-->
    <el-dialog :title="role.name" :visible.sync="visible" @close="$emit('close')" 
               :close-on-click-modal="false">
        <el-form ref="editForm" :model="editForm" :rules="rules" label-width="80px">
            <el-form-item prop="db_user" label="账号">
                <el-input v-model="editForm.db_user" auto-complete="off" :disabled="is_disabled"></el-input>
            </el-form-item>
            <el-form-item prop="db_password" label="密码">
                <el-input type="password" v-model="editForm.db_password" auto-complete="off" :disabled="is_disabled">
                </el-input>
            </el-form-item>
            <el-form-item label="确认密码" prop="checkPass">
                <el-input type="password" v-model="editForm.checkPass" autocomplete="off"></el-input>
            </el-form-item>
            <el-form-item prop="db_database" label="数据库">
                <el-select v-model="editForm.db_database" placeholder="请选择数据库">
                    <el-option v-for="item in items" :key="item" :label="item" :value="item">
                    </el-option>
                </el-select>
            </el-form-item>
            <el-form-item prop="db_priv" label="权限">
                <el-radio v-model="editForm.db_priv" label="0">只读</el-radio>
                <el-radio v-model="editForm.db_priv" label="1">读写</el-radio>
            </el-form-item>
            <el-form-item prop="desc" label="描述">
                <el-input v-model="editForm.desc" auto-complete="off" :disabled="is_disabled"></el-input>
            </el-form-item>
            <el-alert v-if="error" :title="error" type="error" style="margin-top: -10px; margin-bottom: 10px"
                      show-icon></el-alert>
        </el-form>
        <div slot="footer">
            <el-button type="text" @click="visible = false">取消</el-button>
            <el-button type="primary" :loading="btnSaveLoading" @click="saveCommit">保存</el-button>
        </div>
    </el-dialog>
</template>

<style>

</style>

<script>
    export default {
        props: ['role'],
        data () {
            var validatePass2 = (rule, value, callback) => {
            if (value === '') {
              callback(new Error('请再次输入密码'));
            } else if (value !== this.editForm.db_password) {
              callback(new Error('两次输入密码不一致!'));
            } else {
              callback();
            }
          };
            return {
                editFormTitle: '',
                is_disabled: false,
                editForm: {
                    'user_id':'',
                    'db_user':'',
                    'db_password':'',
                    'desc':'',
                    'db_database':'',
                    'db_priv': '0'
                },
                rules: {
                    db_user: [
                        {required: true, message: '请输入账号', trigger: 'blur'}
                    ],
                    db_password: [
                        {required: true, message: '请输入密码', trigger: 'blur'}
                    ],
                    checkPass: [
                        { validator: validatePass2, required: true,trigger: 'blur' }
                     ],
                    db_database: [
                        {required: true, message: '请输入数据库名称', trigger: 'blur'}
                    ],
                    db_priv: [
                        {required: true, message: '请选择数据库权限', trigger: 'blur'}
                    ]
                },
                error: false,
                items: [],
                visible: true,
                loading: false,
                btnSaveLoading: false,
                codes: undefined,
                show: false,
                checkPass: ''
            }
        },
        methods: {

            //判断渲染，true:暗文显示，false:明文显示
            changePass(value) {
                this.show = !(value === 'show');
            },   
            // 获取数据库列表
            get_db_fetch() {
                this.loading = true;
                this.$http.get(`/api/users/user_info/${this.role.id}/database/`).then(res => {
                    this.items = res.result
                }, res => this.$layer_message(res.result)).finally(() => this.loading = false)
            },
           
           // 提交按钮
            saveCommit() {
                /*this.btnSaveLoading = true;
                this.editForm.user_id = this.role.id;
                this.$http.post(`/api/users/user_info/`, this.editForm).then(() => {
                    this.visible = false
                }, res => this.$layer_message('提交成功', 'success')).finally(() => this.btnSaveLoading = false);*/

                this.btnSaveLoading = true;
                this.editForm.user_id = this.role.id;
                let request;
                request = this.$http.post(`/api/users/user_info/`, this.editForm)
                request.then(() => {
                    this.visible = false;
                    this.$layer_message('提交成功', 'success');
                    this.get_db_fetch();
                }, res => this.$layer_message(res.result)).finally(() => this.btnSaveLoading = false)
            }
        },
        mounted() {
            this.get_db_fetch()
        }

    }
</script>
