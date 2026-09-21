'use client'
import {Context} from '../../providers/tanstack'
import {
  useQuery,
  useMutation,
  useQueryClient,
  QueryClient,
  QueryClientProvider,
  useIsFetching
} from '@tanstack/react-query'
import React, { useState, useContext, useEffect } from "react";
import Sidebar from '../sidebar'
import FilesModelsCard from '../files-and-models'
import JobQueueCard from '../job_queue'
import ProjectsJoined from '../projects-joined'
import DatasetsTable from './datasets-table'
import AnnImg_detailed from '../annImg-detailed-view'
interface RecentUserContents {
  image_name: string;
  training_img: string;
  updated_at: string;
  annotations: [];
}
export default function DatasetMain({session}){
const queryClient = useQueryClient()
        const { isPending, error,  data, isFetching } = useQuery({ queryKey: ['db_contents'],retry: 3, refetchInterval: 5000, enabled: Boolean(session.user),
            queryFn: async () => {
            const res = await fetch(`/api/auth/db_recents`,)

            return await res.json()
            },
        });
        useEffect(() => {
            if(!data) return;
            //console.log("db_data gotten to frontend", data)

        }, [data]);
    const RecentUserContents_setted: RecentUserContents[] = data != undefined && data.length != 0  ? data : [];
    const updatedByLabel = session.user?.username ?? session.user?.email ?? "Unknown user";
    const [open_clickedAnnImg_content, setopen_clickedAnnImg_content] = useState(false)
    const [specified_AnnImg_content,setSpecified_AnnImg_content] = useState([]);
    if(open_clickedAnnImg_content === false && specified_AnnImg_content.length != 0){
        specified_AnnImg_content.length = 0;
    }

    return(
        <div className="flex h-full bg-white">
        {RecentUserContents_setted != undefined && (
            <>
          <Sidebar
            recentThumbnails={RecentUserContents_setted.slice(0, 4).map((item) => ({
              id: item.id,
              training_img: item.training_img,
              alt: item.image_name,
            }))}
          />

          <main className="flex-1 px-8 py-6">
            <div className="grid grid-cols-1 gap-6 lg:grid-cols-[2fr_1fr]">
              <div className="flex flex-col gap-6">
                <FilesModelsCard />
                <DatasetsTable
                  RecentUserContents={RecentUserContents_setted}
                  users_near_real_time={session.user.created_at}
                  isLoading={isPending}
                  isError={Error}
                  updatedByLabel={updatedByLabel}
                  setopen_clickedAnnImg_content={setopen_clickedAnnImg_content}
                  setSpecified_AnnImg_content={setSpecified_AnnImg_content}
                />
              </div>

              <div className="flex flex-col gap-6">
                {/* No jobs data source yet — see JobQueueCard.tsx for how this
                    is meant to be filled in later. */}
                <JobQueueCard />
                {/* Same story for shared projects. */}
                <ProjectsJoined />
              </div>
            </div>
          </main>
          </>
          )}
      </div>
    );
}

