
"use client";

import { useMemo, useState, useEffect, type ReactNode } from "react";
import { formatUpdatedAt} from "@/app/lib/formatUpdateAt.ts";

interface RecentlyAddedCardProps {
  users_near_real_time: int;
  isLoading: boolean;
  updatedByLabel: string;
}

export default function RecentlyAddedCard({
  RecentUserContents,
  users_near_real_time,
  isLoading,
  updatedByLabel,
  setopen_clickedAnnImg_content,
  setSpecified_AnnImg_content,
}: RecentlyAddedCardProps) {
  const [query, setQuery] = useState("");
  const [recent_data_selected_to_dataset, setRecent_data_selected_to_dataset] = useState([]);
  const [all_selected_checkbox, setAll_selected_checkbox] = useState(false);
  //const [perPaged_RecentContent, setperPaged_RecentContent] = useState([])
  const [looped_amount, setlooped_amount] = useState([])
  const filtered_RecentUserContents = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return RecentUserContents;
    return RecentUserContents.filter((invi) => invi.image_name.toLowerCase().includes(q));
  }, [RecentUserContents, query]);

  const [clickedPage_Index, setClickedPage_Index] = useState(0);

  const items_wanted_perPage = 3;
  const totalPages = Math.ceil(
      RecentUserContents.length / items_wanted_perPage
  );

  const perPaged_RecentContent = RecentUserContents.slice(
    clickedPage_Index * items_wanted_perPage,
    (clickedPage_Index + 1) * items_wanted_perPage
  );

  const users_time = new Date(users_near_real_time * 1000)
  function toggleAll() {
      console.log("getting all")
      for(let i = 0; i < RecentUserContents.length; i++){
          let currently_in_data =  RecentUserContents[i];
          console.log("i is currently", currently_in_data)
          let found_by_id = recent_data_selected_to_dataset.find(
        invi_in_chosen_list => invi_in_chosen_list.id === currently_in_data.id
      );

      console.log("found_by_id", found_by_id);

      if (found_by_id === undefined) {
        console.log("adding entry to popup", currently_in_data);
        setAll_selected_checkbox(true)
        setRecent_data_selected_to_dataset(prev => [...prev, currently_in_data]);
      } else {
        console.log("delete entry from popup", currently_in_data);
        setAll_selected_checkbox(false)
        setRecent_data_selected_to_dataset(prev =>
          prev.filter(invi_in_chosen_list => invi_in_chosen_list.id !== currently_in_data.id)
        );
      }
      }
  }

  function settingSelected_from_recently_added(clicked_item) {
  console.log("toggleOne index_number", clicked_item.id);

  let found_by_id = recent_data_selected_to_dataset.find(
    invi_in_chosen_list => invi_in_chosen_list.id === clicked_item.id
  );

  console.log("found_by_id", found_by_id);

  if (found_by_id === undefined) {
    console.log("adding entry to popup", clicked_item);

    setRecent_data_selected_to_dataset(prev => [...prev, clicked_item]);
  } else {
    console.log("delete entry from popup", clicked_item);

    setRecent_data_selected_to_dataset(prev =>
      prev.filter(invi_in_chosen_list => invi_in_chosen_list.id !== clicked_item.id)
    );
  }
}

  return (
    <section aria-label="Recently added" className="rounded-2xl bg-neutral-100 p-4">
      <div className="flex flex-wrap items-center gap-4 pl-2">
        <label className="flex items-center gap-2 text-sm font-medium text-neutral-700">
          <input
            type="checkbox"
            onChange={toggleAll}
            checked={all_selected_checkbox === true}
            aria-label="Select all recently added files"
          />
          Recently added
        </label>
        <span className="text-sm text-neutral-500">Selected files {recent_data_selected_to_dataset.size}</span>
        <input
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search available images"
          className="ml-auto min-w-[220px] rounded-full border border-neutral-300 bg-white px-4 py-1.5 text-sm outline-none focus:border-neutral-500"
        />
      </div>
      {recent_data_selected_to_dataset.length != 0 && <div className="pl-4 flex">{recent_data_selected_to_dataset.map((invidual =>
          {
              let third_backspace_in_img_name = invidual.image_name.indexOf("/", 30)
                  //console.log("third_backspace_in_img_name", third_backspace_in_img_name)
                  let showable_name_to_user = invidual.image_name.slice(third_backspace_in_img_name+1)
              return(<div className="bg-blue-100/80 mr-2 flex rounded-t-lg px-2 cursor-pointer" key={invidual.id}><p onClick={()=> setopen_clickedAnnImg_content(true) & setSpecified_AnnImg_content(prev => [...prev, invidual])}>{showable_name_to_user}</p>
                  <p className="pl-2 pr-2 text-slate-400" onClick={(()=> settingSelected_from_recently_added(invidual))}>x</p>
                  </div>
          )}))}
          </div>
      }

      <div className="overflow-x-auto min-h-50">
        <table className="w-full border-collapse text-left text-sm">
          <thead>
            <tr className="border-b border-neutral-200 text-neutral-500">
              <th className="w-8 py-2 font-normal" />
              <th className="py-2 font-normal">File Name</th>
              <th className="py-2 font-normal">File Size</th>
              <th className="py-2 font-normal">Last Changed</th>
              <th className="py-2 font-normal">Updated by</th>
              <th className="w-10 py-2 font-normal">Actions</th>
            </tr>
          </thead>
          <tbody>
            {isLoading && <RowMessage colSpan={6}>Loading recently added files&hellip;</RowMessage>}

            {!isLoading && RecentUserContents.length === 0 && (
              <RowMessage colSpan={6}>Couldn&apos;t load your recent files. Try refreshing the page.</RowMessage>
            )}

            {!isLoading && RecentUserContents.length === 0 && (
              <RowMessage colSpan={6}>
                {RecentUserContents.length === 0
                  ? "No files yet — predictions you run will show up here."
                  : "No files match your search."}
              </RowMessage>
            )}

            {!isLoading &&
              perPaged_RecentContent.map((item) => {
                  let is_relatively_new_addition = false;
                  let current_items_time = new Date(item.updated_at);
                  let found_by_id_in_selected_checkbox = false;
                  let third_backspace_in_img_name = item.image_name.indexOf("/", 30)
                  //console.log("third_backspace_in_img_name", third_backspace_in_img_name)
                  let showable_name_to_user = item.image_name.slice(third_backspace_in_img_name+1)
                  //let sum_of_times = current_items_time - users_time;
                  if(current_items_time.getFullYear() === users_time.getFullYear()){
                    if(current_items_time.getMonth() +1 === users_time.getMonth()+1){
                        if(current_items_time.getDay() -1 === users_time.getDay()-1){
                            if(current_items_time.getHours() === users_time.getHours()){
                                is_relatively_new_addition = true;
                            }
                        }
                    }
                  }
                const found_by_id_in_selected = recent_data_selected_to_dataset.find(invi_in_chosen_list => invi_in_chosen_list.id === item.id)
                  //console.log("sum_of_times", sum_of_times)
                if(found_by_id_in_selected != undefined){
                    found_by_id_in_selected_checkbox = true
                } else {
                    found_by_id_in_selected_checkbox = false;
                }


                return(
                <tr key={item.id} className={`${found_by_id_in_selected ? 'bg-neutral-200/50' : 'bg-neutral-100'} hover:bg-neutral-300/50 border-b border-neutral-200 last:border-0`} onClick={()=> settingSelected_from_recently_added(item)}>
                  <td className="py-3 pl-2">
                    <input
                      type="checkbox"
                      checked={found_by_id_in_selected_checkbox}
                      onChange={e => found_by_id_in_selected_checkbox ===true}
                      aria-label={`Select ${item.image_name}`}
                    />
                  </td>
                  <td className="py-3 text-neutral-800">{showable_name_to_user}</td>
                  {/* File size is hardcoded per current requirements — the
                      API doesn't report it yet. See review notes. */}
                  <td className="py-3 text-neutral-500">1gb</td>
                  {is_relatively_new_addition ? <><td className="flex py-3 text-neutral-900">{current_items_time.toLocaleTimeString()}
                  <p className="bg-blue-400 w-2 h-2 rounded-full animate-ping"></p></td></>
                  :
                  <td className="py-3 text-neutral-500">{formatUpdatedAt(item.updated_at)}</td>
                  }
                  <td className="py-3">
                    <div className="flex items-center gap-2">
                      <span className="h-6 w-6 rounded-full bg-neutral-300" aria-hidden />
                      <span className="text-neutral-600">{updatedByLabel}</span>
                    </div>
                  </td>
                  <td className="py-3 text-neutral-400">&middot;&middot;&middot;</td>
                </tr>
                );
              })}
          </tbody>
        </table>
      </div>
      <div className="ml-4 flex gap-1 mt-2">
      {Array.from({ length: totalPages }).map((_, i) => (
          <button
            key={i}
            onClick={() => setClickedPage_Index(i)}
            className={`w-4 h-4 rounded-full ${
              clickedPage_Index === i ? "bg-blue-400" : "bg-blue-300"
            }`}
          />
      ))}
      </div>
    </section>
  );
}

function RowMessage({ children, colSpan }: { children: ReactNode; colSpan: number }) {
  return (
    <tr>
      <td colSpan={colSpan} className="py-8 text-center text-sm text-neutral-400">
        {children}
      </td>
    </tr>
  );
}