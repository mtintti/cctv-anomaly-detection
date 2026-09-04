import { Toast } from '@base-ui/react/toast';
import styles from './stacked-notifications.module.css'

interface isnonStandardNotification {
  error_message?: string;
  message_with_link?: string;
}

function isnonStandardNotification(
  toast: Toast.Root.ToastObject,
): toast is Toast.Root.ToastObject<isnonStandardNotification> {
  if (toast.data?.error_message !== undefined){
      return toast.data?.error_message;
  }
  if (toast.data?.message_with_link !== undefined){
      return toast.data?.message_with_link;
  }
}

export function StackedNotifications(){
    const { toasts } = Toast.useToastManager();
    console.log('TOASTs:', toasts);
    return(
     <Toast.Portal>
      <Toast.Viewport className={styles.StackedViewport}>
        {toasts.map((toast) => (
          <Toast.Root key={toast.id} toast={toast} className={styles.StackedToast}>
            <Toast.Content className={styles.Content}>
              <div className={styles.Text}>
              {isnonStandardNotification(toast) && toast.data ?
              <>

                    {toast.data?.message_with_link !== undefined && <>
                    <Toast.Title className={styles.Title} />
                        <Toast.Description className={styles.Description}>
                            {toast.data.message_with_link}
                        </Toast.Description>
                    </>}

                    {toast.data?.error_message !== undefined && <>
                        <Toast.Title className={styles.Title_error} />
                        <Toast.Description className={styles.Description_error}>
                            {toast.data.error_message}
                        </Toast.Description>
                    </>}
              </>
                :
                <>
                <Toast.Title className={styles.Title} />
                <Toast.Description className={styles.Description} />
              </>
              }
              </div>
              <Toast.Close className={styles.Close}>Dismiss</Toast.Close>
            </Toast.Content>
          </Toast.Root>
        ))}
      </Toast.Viewport>
    </Toast.Portal>
    )
}