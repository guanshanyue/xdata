<template>
    <!--编辑新增界面-->
    <el-dialog :title="role.name" :visible.sync="visible" @close="$emit('close')"  width="80%"
               :close-on-click-modal="false">
        <el-row>
            <el-col :span="16">
                <el-form :inline="true" :model="host_query">
                    <el-form-item>
                        <el-input v-model="host_query.name_field" clearable placeholder="账号名称"></el-input>
                    </el-form-item>
                    <el-form-item>
                        <el-button type="primary" icon="search" @click="fetch()">查询</el-button>
                    </el-form-item>
                </el-form>
            </el-col>
            <el-col :span="8"  style="text-align: right">
                <el-button @click="refresh()">刷新</el-button>
                <!-- <el-button v-if="has_permission('users_info_add')" type="primary" @click="handleAdd">添加账号</el-button> -->
            </el-col>
        </el-row>
        <el-table :data="hosts.data" v-loading="tableLoading" style="width: 100%; margin-top: 20px">
            <el-table-column prop="db_user" label="账号名称" width="160px"></el-table-column>
            <el-table-column prop="db_database" label="所属数据库" width="160px"></el-table-column>
            <el-table-column prop="db_priv" label="权限" width="160px"></el-table-column>
            <el-table-column prop="desc" label="账号描述" width="160px"></el-table-column>
            <el-table-column label="操作" width="400px" v-if="has_permission('users_info_edit|users_info_del|users_info_valid')">
                <template slot-scope="scope">
                    <el-button v-if="has_permission('users_info_edit')" size="small" @click="handleEdit(scope.row)">
                        重置密码
                    </el-button>
                    <el-button v-if="has_permission('users_info_edit')" size="small" type="primary" @click="handleChange(scope.row)"
                               >修改权限
                    </el-button>
                    <el-button v-if="has_permission('users_info_del')" size="small" type="danger" @click="deleteCommit(scope.row)"
                               :loading="btnDelLoading[scope.row.priv_id]">删除
                    </el-button>
                </template>
            </el-table-column>
        </el-table>
        <!--分页-->
        <div class="pagination-bar" v-if="hosts.total > 10">
            <el-pagination
                    @current-change="handleCurrentChange"
                    :current-page="currentPage"  layout="total, prev, pager, next"
                    :total="hosts.total">
            </el-pagination>
        </div>
        <el-dialog :title="title" :visible.sync="dialogVisible" width="80%" append-to-body>
            <el-form :model="form"  :rules="rules" label-width="80px">
                <el-form-item prop="db_password" label="密码">
                <el-input type="password" v-model="form.new_password" auto-complete="off" :disabled="is_disabled">
                </el-input>
            </el-form-item>
            <el-form-item label="确认密码" prop="checkPass">
                <el-input type="password" v-model="form.checkPass" autocomplete="off"></el-input>
            </el-form-item>
            </el-form>
            <div slot="footer">
                <el-button @click="dialogVisible=false">取消</el-button>
                <el-button type="primary" @click="resetCommit" :loading="btnSaveLoading">保存</el-button>
            </div>
        </el-dialog>
        <el-dialog :title="title" :visible.sync="dialogChaPriVisible" width="80%" append-to-body>
            <el-form :model="privformedit" label-width="80px">
                <el-form-item prop="db_priv" label="权限">
                    <el-radio v-model="privformedit.db_priv" label="只读">只读</el-radio>
                    <el-radio v-model="privformedit.db_priv" label="读写">读写</el-radio>
                </el-form-item>
            </el-form>
            <div slot="footer">
                <el-button @click="dialogChaPriVisible=false">取消</el-button>
                <el-button type="primary" @click="privCommit" :loading="btnSaveLoading">保存</el-button>
            </div>
        </el-dialog>
        <!-- <change-priv v-if="dialogChaPriVisible" :privrole="privformedit" @close="dialogChaPriVisible = false"></change-priv> -->
    </el-dialog>
</template>

<style>

</style>

<script>
    import ChangePriv from './ChangePriv.vue'
    export default {
        props: ['role'],
        components: {
            ChangePriv,
        },
        data () {
            var validatePass2 = (rule, value, callback) => {
            if (value === '') {
              callback(new Error('请再次输入密码'));
            } else if (value !== this.form.new_password) {
              callback(new Error('两次输入密码不一致!'));
            } else {
              callback();
            }
          };
            return {
                editFormTitle: '',
                visible: true,
                is_disabled: false,
                host_query: {
                    user_id: '',
                    name_field: ''
                },
                currentPage: 1,
                hosts: [],
                tableLoading: true,
                btnDelLoading: {},
                dialogVisible: false,
                title:'1',
                btnSaveLoading: false,
                activeName:'first',
                form: {
                    'new_password':''
                },
                show: false,
                rules: {
                    new_password: [
                        {required: true, message: '请输入密码', trigger: 'blur'}
                    ],
                    checkPass: [
                        { validator: validatePass2, required: true,trigger: 'blur' }
                     ]
                },
                formedit: '',
                privformedit: {},
                is_disabled: false,
                checkPass: '',
                dialogChaPriVisible: false,
                delformedit: ''
            }
        },
        methods: {

            handleCurrentChange(val) {
                this.currentPage = val;
                this.fetch(this.currentPage);
            },
            fetch (page) {
                if (!page) page = 1;
                this.tableLoading = true;
                this.host_query.user_id = this.role.id
                let api_uri = '/api/users/user_info/';
                this.$http.get(api_uri, {params: {page: page, host_query: this.host_query}}).then(res => {
                    this.hosts = res.result
                }, res => this.$layer_message(res.result)).finally(() => this.tableLoading = false)
            },

            //刷新
            refresh(){
                this.fetch(this.currentPage);
            },

            //重置密码
            handleEdit (row) {
                this.formedit = this.$deepCopy(row);
                this.dialogVisible = true;
                this.title = '重置密码';
            },

             //修改权限
            handleChange (row) {
                this.privformedit = this.$deepCopy(row);
                this.dialogChaPriVisible = true;
                this.title = '修改权限';
            },

            //提交修改
            resetCommit () {
                if (this.form.new_password === this.form.checkPass) {
                    this.btnSaveLoading = true;
                    let request;
                    request = this.$http.put(`/api/users/user_info/${this.formedit.account_id}/reset_password/`,this.form)
                    request.then(() => {
                        this.dialogVisible = false;
                        this.$layer_message('提交成功', 'success');
                    }, res => this.$layer_message(res.result)).finally(() => this.btnSaveLoading = false)
                }
            },

            //修改权限
            privCommit () {
                this.btnSaveLoading = true;
                let request;
                request = this.$http.put(`/api/users/user_info/${this.privformedit.priv_id}/change_privileges/`,this.privformedit)
                request.then(() => {
                    this.dialogChaPriVisible = false;
                    this.$layer_message('提交成功', 'success');
                }, res => this.$layer_message(res.result)).finally(() => this.btnSaveLoading = false)
                this.refresh()
            },

            // 删除权限
            deleteCommit (row) {
                // this.delformedit = this.$deepCopy(row);
                this.$confirm('此操作将删除访问该数据库的权限，是否继续？', '删除确认', {type: 'warning'}).then(() => {
                    this.btnDelLoading = {[row.priv_id]: true};
                    this.$http.delete(`/api/users/user_info/${row.priv_id}`).then(() => {
                        this.fetch(this.currentPage)
                    }, res => this.$layer_message(res.result)).finally(() => this.btnDelLoading = {})
                }).catch(() => {
                })
            }    
        },
        mounted() {
            this.fetch()
            //this.get_db_fetch()
        }

    }
</script>
