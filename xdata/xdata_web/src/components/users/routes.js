/**
 * Created by aka on 2017/5/22.
 */


import User from './User.vue';
import Mongodb from './Mongodb.vue';

export default [
    {
        path: 'user',
        component: User,
        meta: {
            permission: 'users_host_view'
        }
    },
    {
        path: 'mongodb',
        component: Mongodb,
        meta: {
            permission: 'users_mongodb_view'
        }
    },
]
