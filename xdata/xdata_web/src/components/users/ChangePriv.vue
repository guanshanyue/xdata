<template>
    <el-dialog title="修改权限" :visible.sync="visible" @close="$emit('close')" append-to-body>
            <el-transfer :titles="['可选权限', '已分配权限']"  
                style="text-align: left; display: inline-block"
                filterable
                :format="{
                    noChecked: '${total}',
                    hasChecked: '${checked}/${total}'
                }"
                v-model="priv_result" :data="privs"></el-transfer>
            <div slot="footer" v-if="has_permission('users_info_edit')">
                <el-button @click="visible = false">取消</el-button>
                <el-button type="primary" @click="saveCommit" :loading="btnSaveLoading">保存</el-button>
            </div>
    </el-dialog>
</template>

<script>

    export default {
        props: ['privrole'],
        data() {
            return {
                visible: true,
                priv_result: [],
                privs: [],
                btnSaveLoading: false
            }
        },
        methods: {
            get_db_fetch () {
                this.$http.get(`/api/users/user_info/${this.privrole.account_id}/database/valid/`).then(res => {
                    for (let item of res.result) {
                        this.privs.push({
                            key: String(item.id),
                            label: item.name
                        })
                        if (item.status === '1') {
                            this.priv_result.push(String(item.id))
                        }
                    }
                }, res => this.$layer_message(res.result)).finally(() => this.loading = false)
            },
            saveCommit() {
                this.btnSaveLoading = true;
                this.$http.post(`/api/account/roles/${this.role.id}/permissions/publish`, {app_ids: this.app_result, env_ids: this.env_result}).then(() => {
                    this.visible = false
                }, res => this.$layer_message(res.result)).finally(() => this.btnSaveLoading = false)
            }
        },
        mounted() {
            this.get_db_fetch()
            //this.get_db_fetch()
        }
    }
</script>