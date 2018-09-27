<template>
    <div>
        <el-row>
            <el-col :span="16">
                <el-form :inline="true" :model="host_query">
                    <el-form-item>
                        <el-input v-model="host_query.name_field" clearable placeholder="数据库名称"></el-input>
                    </el-form-item>
                    <el-select v-model="host_query.zone_field" @change="zone_Search()" clearable placeholder="所在区域">
                        <el-option v-for="item in zone_options" :key="item" :value="item"></el-option>
                    </el-select>
                    <el-select v-model="host_query.type_field" @change="type_Search()" clearable placeholder="数据库类型">
                        <el-option v-for="item in type_options" :key="item" :value="item"></el-option>
                    </el-select>
                    <el-form-item>
                        <el-button type="primary" icon="search" @click="fetch()">查询</el-button>
                    </el-form-item>
                </el-form>
            </el-col>
            <el-col :span="8"  style="text-align: right">
                <el-button @click="refresh()">刷新</el-button>
                <el-button v-if="has_permission('users_host_add')" type="primary" @click="handleAdd">添加数据库</el-button>
            </el-col>
        </el-row>
        <el-table :data="hosts.data" @expand-change="get_host_extend" v-loading="tableLoading" style="width: 100%; margin-top: 20px">
            <el-table-column type="expand">
                <template slot-scope="props">
                    <el-form v-if="props.row.extend" label-position="left" inline class="demo-table-expand">
                        <el-form-item label="所属区域"><span>{{ props.row.extend.zone }}</span></el-form-item>
                        <el-form-item label="数据库类型"><span>{{ props.row.extend.type }}</span></el-form-item>
                        <el-form-item label="数据库名称"><span>{{ props.row.extend.name }}</span></el-form-item>
                        <el-form-item label="数据库地址"><span>{{ props.row.extend.db_host }}</span></el-form-item>
                        <el-form-item label="数据库账号"><span>{{ props.row.extend.db_user }}</span></el-form-item>
                        <el-form-item label="数据库端口"><span>{{ props.row.extend.db_user }}</span></el-form-item>
                        <el-form-item label="备注信息"><span>{{ props.row.desc }}</span></el-form-item>
                    </el-form>
                    <el-row v-else style="text-align: center">
                        <span style="color: #99a9bf">暂没有配置信息，点击验证自动获取...</span>
                    </el-row>
                </template>
            </el-table-column>

            <el-table-column prop="name" label="数据库名称" width="160px"></el-table-column>
            <el-table-column prop="zone" label="所属区域" width="160px"></el-table-column>
            <el-table-column prop="type" label="数据库类型" width="160px"></el-table-column>
            <el-table-column prop="db_host" label="数据库地址" width="160px"></el-table-column>
            <el-table-column label="操作" width="400px" v-if="has_permission('users_host_edit|users_host_del|users_host_valid')">
                <template slot-scope="scope">
                    <el-button v-if="has_permission('users_host_edit')" size="small" @click="handleEdit(scope.row)">编辑</el-button>
                    <el-button v-if="has_permission('users_info_add')" size="small" type="primary" @click="userAdd(scope.row)"
                               >新增用户
                    </el-button>
                    <el-button v-if="has_permission('users_info_edit')" size="small" type="primary" @click="userEdit(scope.row)"
                               >管理
                    </el-button>
                    <el-button v-if="has_permission('users_host_valid')" size="small" type="success" @click="valid(scope.row)"
                               :loading="btnValidLoading[scope.row.id]">验证
                    </el-button>
                    <el-button v-if="has_permission('users_host_del')" size="small" type="danger" @click="deleteCommit(scope.row)"
                               :loading="btnDelLoading[scope.row.id]">删除
                    </el-button>
                </template>
            </el-table-column>
        </el-table>
        <adduser v-if="dialogPerVisible" :role="formuser" @close="dialogPerVisible = false"></adduser>
        <userinfo v-if="dialogUserInfoVisible" :role="formuserinfo" @close="dialogUserInfoVisible = false"></userinfo>
        <!--分页-->
        <div class="pagination-bar" v-if="hosts.total > 10">
            <el-pagination
                    @current-change="handleCurrentChange"
                    :current-page="currentPage"  layout="total, prev, pager, next"
                    :total="hosts.total">
            </el-pagination>
        </div>

        <el-dialog :title="title" :visible.sync="dialogVisible" width="80%" :close-on-click-modal="false">
            <el-tabs v-model="activeName" >
                <el-tab-pane label="单条记录" name="first">
                    <el-form :model="form" label-width="80px">
                        <el-form-item label="所属区域" prop="zone" required>
                            <el-select v-model="form.zone" placeholder="所在区域">
                                <el-option v-for="z in zone_options" :value="z" :key="z"></el-option>
                            </el-select>
                            <el-button style="margin-left: 15px" type="text" @click="addZone">添加区域</el-button>
                        </el-form-item>
                        <el-form-item label="数据库类型" prop="type" required>
                            <el-select v-model="form.type" placeholder="数据库类型">
                                <el-option v-for="t in type_options" :value="t" :key="t"></el-option>
                            </el-select>
                            <el-button style="margin-left: 15px" type="text" @click="addType">添加类型</el-button>
                        </el-form-item>
                        <el-form-item label="数据库名称" prop="name" required>
                            <el-input v-model="form.name"></el-input>
                        </el-form-item>
                        <el-form-item label="数据库地址" prop="db_host"  required>
                            <el-input v-model="form.db_host"></el-input>
                        </el-form-item>
                        <el-form-item label="数据库账号" prop="db_user" required>
                            <el-input v-model="form.db_user"></el-input>
                        </el-form-item>
                        <el-form-item  label="数据库密码" prop="db_password" required>
                            <el-input type="password" v-model="form.db_password"></el-input>
                        </el-form-item>
                        <el-form-item label="数据库端口" prop="db_port" required>
                            <el-input v-model="form.db_port"></el-input>
                        </el-form-item>
                        <el-form-item label="备注信息" prop="desc">
                            <el-input v-model="form.desc" type="textarea" autosize></el-input>
                        </el-form-item>
                    </el-form>
                </el-tab-pane>

                <el-tab-pane label="批量导入" name="second" v-if="importStatus" v-loading="import_loading" element-loading-text="正在导入...">
                    <a :href= "download_url" download="host.xls">批量导入模板下载.xls</a>
                    <div class="el-upload__tip"></div>
                    <el-upload ref="upload" action="" :http-request="import_submit" name="file" :multiple="false"
                               :before-upload="beforeAvatarUpload" :file-list="fileList">
                        <el-button size="small" type="primary" v-if="has_permission('users_host_add')">点击批量导入</el-button>
                        <div slot="tip" class="el-upload__tip">只能上传xls/xlsx文件</div>
                    </el-upload>
                </el-tab-pane>
            </el-tabs>

            <div slot="footer">
                <el-button @click="dialogVisible=false">取消</el-button>
                <el-button type="primary" @click="saveCommit" :loading="btnSaveLoading">保存</el-button>
            </div>
        </el-dialog>
    </div>
</template>


<style>
    .demo-table-expand {
        font-size: 0;
    }
    .demo-table-expand label {
        width: 90px;
        color: #99a9bf;
    }
    .demo-table-expand .el-form-item {
        margin-right: 0;
        margin-bottom: 0;
        width: 50%;
    }
</style>

<script>
    import envs from '../../config/env'
    import Adduser from './Adduser.vue'
    import UserInfo from './UserInfo.vue'
    export default {
        components: {
            adduser: Adduser,
            userinfo: UserInfo
        },
        data () {
            return {
                host_zone: '',
                host_query: {
                    name_field: '',
                    zone_field: '',
                    type_field: ''
                },
                dialogVisible: false,
                btnSaveLoading: false,
                btnDelLoading: {},
                btnValidLoading: {},
                tableLoading: true,
                form: { zone: '' ,type: ''},
                hosts: [],
                currentPage: 1,
                zone_options: [],
                type_options: [],
                file_name: 'file',
                title: '编辑主机',
                activeName:'first',
                importStatus: false,
                fileList: [],
                tp_file:'',
                import_loading: false,
                download_url: envs.apiServer + "/apis/files/download/host.xls",
                formuser: {},
                dialogPerVisible: false,
                formuserinfo: {},
                dialogUserInfoVisible: false
            }
        },
        methods: {
            handleCurrentChange(val) {
                this.currentPage = val;
                this.fetch(this.currentPage);
            },

            //区域查询
            zone_Search(){
                this.currentPage = 1;
                this.fetch();
            },

            //刷新
            refresh(){
                this.fetch(this.currentPage);
            },

            //新增用户
            userAdd(row) {
                this.formuser = this.$deepCopy(row);
                this.dialogPerVisible = true;
            },

            //管理用户
            userEdit(row) {
                this.formuserinfo = this.$deepCopy(row);
                this.dialogUserInfoVisible = true;
            },

            //获取区域
            get_host_zone () {
                this.$http.get('/api/users/hosts/zone/').then(res => {
                    this.zone_options = res.result
                }, res => this.$layer_message(res.result))
            },

            //获取数据库类型
            get_host_type () {
                this.$http.get('/api/users/hosts/type/').then(res => {
                    this.type_options = res.result
                }, res => this.$layer_message(res.result))
            },

            fetch (page) {
                if (!page) page = 1;
                this.tableLoading = true;
                let api_uri = '/api/users/hosts/';
                this.$http.get(api_uri, {params: {page: page, host_query: this.host_query}}).then(res => {
                    this.hosts = res.result
                }, res => this.$layer_message(res.result)).finally(() => this.tableLoading = false)
            },

            get_host_extend (row, expanded) {
                if (expanded) {
                    this.$http.get(`/api/users/hosts/${row.id}/extend/`).then(res => {
                        this.$set(row, 'extend', res.result)
                    }, res => this.$layer_message(res.result))
                }
            },
            beforeAvatarUpload: function (file) {
                if (['application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'].indexOf(file.type) == -1) {
                    this.$layer_message('请上传xls, xlsx格式的文件');
                    return false
                }
            },

            import_submit(data){
                this.import_loading = true;
                var excel_file = new FormData();
                excel_file.append('file', data.file);
                this.$http.post(`/api/users/hosts/import`, excel_file).then(res => {
                    this.import_loading=false;
                    this.dialogVisible = false;
                    this.$refs.upload.clearFiles();
                    this.$layer_message(res.result, 'success');
                }, res => this.$layer_message(res.result));
            },

            handleAdd () {
                this.form = {zone: '',type: ''};
                this.title = '添加主机';
                this.dialogVisible = true;
                this.importStatus = true;
            },

            handleEdit (row) {
                this.form = this.$deepCopy(row);
                this.dialogVisible = true;
                this.title = '编辑主机';
                this.importStatus = false;
            },
            saveCommit () {
                this.btnSaveLoading = true;
                let request;
                if (this.form.id) {
                    request = this.$http.put(`/api/users/hosts/${this.form.id}`, this.form)
                } else {
                    request = this.$http.post(`/api/users/hosts/`, this.form)
                }
                request.then(() => {
                    this.dialogVisible = false;
                    this.$layer_message('提交成功', 'success');
                    this.fetch(this.currentPage);
                    this.get_host_zone();
                    this.get_host_type()
                }, res => this.$layer_message(res.result)).finally(() => this.btnSaveLoading = false)
            },
            deleteCommit (row) {
                this.$confirm('此操作将永久删除该主机，是否继续？', '删除确认', {type: 'warning'}).then(() => {
                    this.btnDelLoading = {[row.id]: true};
                    this.$http.delete(`/api/users/hosts/${row.id}`).then(() => {
                        this.fetch(this.currentPage)
                    }, res => this.$layer_message(res.result)).finally(() => this.btnDelLoading = {})
                }).catch(() => {
                })
            },
            valid (row) {
                this.btnValidLoading = {[row.id]: true};
                this.$http.get(`/api/users/hosts/${row.id}/valid`).then(() => {
                    this.$layer_message('验证通过', 'success');
                    this.btnValidLoading = {};
                }, res => {
                    this.btnValidLoading = {};
                    this.$layer_message(res.result);
                })
            },
            addZone () {
                this.$prompt('请输入主机区域', '提示', {
                    inputPattern: /.+/,
                    inputErrorMessage: '请输入区域！'
                }).then(({value}) => {
                    this.form.zone = value
                }).catch(() => {
                })
            },
            addType () {
                this.$prompt('请输入数据库类型', '提示', {
                    inputPattern: /.+/,
                    inputErrorMessage: '请输入类型！'
                }).then(({value}) => {
                    this.form.type = value
                }).catch(() => {
                })
            },

        },
        created () {
            this.fetch();
            this.get_host_zone();
            this.get_host_type();
        }
    }
</script>