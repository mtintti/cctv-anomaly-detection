export const Fallback_ui = [
  {
    predict_id: 'f7e40404-5d78-40ef-7a70-db1006db4b871',
    jsonresponse: [
      {
        belongsto: 'fallback_1',
        original_img: '/fallback/base_original_fallback1.png',
        img_w: 700,
        img_h: 570,
        details: [
          { class_id: 0, class_name: 'classname', confidence_score: 34.50 },
        ],
        prediction: [
          { imageBbox: '/fallback/bbox_fallback1.png', imageSeg: '/fallback/segmask_fallback1.png' },
        ],
      },
    ],
    metrics:
        { handling: '1000.00', preprocess_to_tensor: '100.00', inference: '120.00', bbox_and_segmask: '40.00', original_img_encode: '460.00', batchlist: '0.30',  encode_img_tag: '3400.00', redis: '100.00' ,whole_runs_time: '5544.00'},
  },
  {
    predict_id: 'a2b3c4d5-...',
    jsonresponse: [
      {
        belongsto: 'fallback_2',
        original_img: '/fallback/base_original_fallback2.png',
        img_w: 700,
        img_h: 570,
        details: [
          { class_id: 0, class_name: 'classname', confidence_score: 53.10 },
        ],
        prediction: [
          { imageBbox: '/fallback/bbox_fallback2.png', imageSeg: '/fallback/segmask_fallback2.png' },
        ],
      },
    ],
    metrics:
      { handling: '1000.00', preprocess_to_tensor: '100.00', inference: '120.00', bbox_and_segmask: '40.00', original_img_encode: '460.00', batchlist: '0.30',  encode_img_tag: '3400.00',redis: '100.00', whole_runs_time: '5544.00'},
  },
];

/*

        predict_id: 'f7e40404-5d78-40ef-7a70-db1006db4b871',
    jsonresponse = [{
        belongsto: 'fallback_1'
        },{
        original_img: '../public/fallback/base_original_fallback1.png'},
        details = [{
            class_id: 0},
            {class_name: 'getting data'},
            {confidence_score: 47.50},
        ],
        prediction: [
            {imageBbox: '../public/fallback/bbox_fallback1.png'},
            {imageSeg: '../public/fallback/segmask_fallback1.png'},
            ],
    ],


jsonresponse = [
        belongsto: 'fallback_2',
        original_img: '../public/fallback/base_original_fallback1.png',
        details[
            class_id: 0,
            class_name: 'getting data',
            confidence_score: 50.54,
        ],
        details = [
                class_id: 0,
                class_name: 'getting data',
                confidence_score: 50.54,
            ],
        prediction =[
            imageBbox: '../public/fallback/bbox_fallback2.png',
            imageSeg: '../public/fallback/segmask_fallback2.png'
            ],
    ],
*/


/* {

    predict_id: 'f7e40404-5d78-40ef-7a70-db1006db4b871',
    jsonresponse = [{
        belongsto: 'fallback_1'
        },{
        original_img: '../public/fallback/base_original_fallback1.png'},
        details = [{
            class_id: 0},
            {class_name: 'getting data'},
            {confidence_score: 47.50},
        ],
        prediction= [
            {imageBbox: '../public/fallback/bbox_fallback1.png'},
            {imageSeg: '../public/fallback/segmask_fallback1.png'},
            ],
    ],
    },
{predict_id: 'f7e40404-5d78-40ef-7a70-db1006db4b871' */