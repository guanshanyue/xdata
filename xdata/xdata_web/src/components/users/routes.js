/**
 * Created by aka on 2017/5/22.
 */


import User from './User.vue';

export default [
    {
        path: 'user',
        component: User,
        meta: {
            permission: 'users_host_view'
        }
    }
]
